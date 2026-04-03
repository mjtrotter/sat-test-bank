import math
from datetime import datetime, timedelta
from typing import List, Tuple, Union

# Constants from Glicko-2 paper and specs/rating-system.md
_DEFAULT_TAU = 0.5  # Controls how much volatility can change over time
_DEFAULT_INITIAL_RATING = 1500.0
_DEFAULT_INITIAL_RD = 350.0
_DEFAULT_INITIAL_VOLATILITY = 0.06
_DEFAULT_RD_FLOOR = 50.0
_DEFAULT_RD_CEILING = 350.0
_DEFAULT_INACTIVITY_PERIOD_DAYS = 14
_DEFAULT_RATING_PERIOD_DAYS = 1 # Not directly used in current update, but good for context

class Glicko2:
    """
    Implements the Glicko-2 rating system.

    Attributes:
        rating (float): The player's Glicko-2 rating.
        rd (float): The player's rating deviation.
        volatility (float): The player's rating volatility.
        tau (float): System constant that constrains the change in volatility.
        last_played (datetime): The last time the rating was updated.
        rd_floor (float): Minimum rating deviation.
        rd_ceiling (float): Maximum rating deviation.
        inactivity_period_days (int): Number of days after which RD starts increasing.
    """

    def __init__(
        self,
        rating: float = _DEFAULT_INITIAL_RATING,
        rd: float = _DEFAULT_INITIAL_RD,
        volatility: float = _DEFAULT_INITIAL_VOLATILITY,
        tau: float = _DEFAULT_TAU,
        last_played: Union[datetime, None] = None,
        rd_floor: float = _DEFAULT_RD_FLOOR,
        rd_ceiling: float = _DEFAULT_RD_CEILING,
        inactivity_period_days: int = _DEFAULT_INACTIVITY_PERIOD_DAYS,
    ):
        if not (rd_floor <= rd <= rd_ceiling):
            # If RD is outside bounds on init, clamp it
            rd = max(rd_floor, min(rd, rd_ceiling))
            
        self.rating = rating
        self.rd = rd
        self.volatility = volatility
        self.tau = tau
        self.last_played = last_played if last_played is not None else datetime.utcnow()
        self.rd_floor = rd_floor
        self.rd_ceiling = rd_ceiling
        self.inactivity_period_days = inactivity_period_days

        # Scale down rating and RD for internal calculations as per Glicko-2
        # Glicko-2 ratings are on a different scale (typically mean 0, SD 1)
        # Standard Glicko-2 scale: rating = (rating - 1500) / 173.7178; rd = rd / 173.7178
        self._q = math.log(10) / 400
        self._glicko2_rating = (self.rating - _DEFAULT_INITIAL_RATING) * self._q
        self._glicko2_rd = self.rd * self._q

    def _g(self, phi: float) -> float:
        """Helper function for the Glicko-2 algorithm."""
        return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

    def _e(self, mu: float, mu_j: float, phi_j: float) -> float:
        """Helper function for the Glicko-2 algorithm."""
        return 1 / (1 + math.exp(-self._g(phi_j) * (mu - mu_j)))

    def _calculate_v(self, opponent_data: List[Tuple[float, float, float]]) -> float:
        """
        Calculates the variance of the improved rating.
        opponent_data: List of (opponent_rating, opponent_rd, outcome)
        """
        v_sum = 0
        for opp_rating, opp_rd, _ in opponent_data:
            opp_g2_rating = (opp_rating - _DEFAULT_INITIAL_RATING) * self._q
            opp_g2_rd = opp_rd * self._q
            g_phi_j = self._g(opp_g2_rd)
            e_val = self._e(self._glicko2_rating, opp_g2_rating, opp_g2_rd)
            v_sum += (g_phi_j**2) * e_val * (1 - e_val)
        return 1 / v_sum

    def _calculate_delta(self, v: float, opponent_data: List[Tuple[float, float, float]]) -> float:
        """
        Calculates the estimated improvement in rating.
        opponent_data: List of (opponent_rating, opponent_rd, outcome)
        """
        delta_sum = 0
        for opp_rating, opp_rd, outcome in opponent_data:
            opp_g2_rating = (opp_rating - _DEFAULT_INITIAL_RATING) * self._q
            opp_g2_rd = opp_rd * self._q
            g_phi_j = self._g(opp_g2_rd)
            e_val = self._e(self._glicko2_rating, opp_g2_rating, opp_g2_rd)
            delta_sum += g_phi_j * (outcome - e_val)
        return v * delta_sum

    def _a_func(self, x: float, delta: float, phi: float, v: float, a: float, tau: float) -> float:
        """Function 'f' from Glicko-2 paper used to find new volatility."""
        exp_x = math.exp(x)
        term1 = exp_x * (delta**2 - phi**2 - v - exp_x) / (2 * (phi**2 + exp_x)**2)
        term2 = (x - a) / tau**2
        return term1 - term2

    def _find_new_volatility(self, delta: float, v: float) -> float:
        """
        Performs the iterative algorithm to find the new volatility.
        This is Step 5 of the Glicko-2 algorithm.
        """
        phi = self._glicko2_rd
        sigma = self.volatility
        tau = self.tau

        a = math.log(sigma**2)
        epsilon = 0.000001  # Convergence tolerance
        
        A = a
        if delta**2 > (phi**2 + v):
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while self._a_func(a - k * tau, delta, phi, v, a, tau) < 0:
                k += 1
            B = a - k * tau

        f_A = self._a_func(A, delta, phi, v, a, tau)
        f_B = self._a_func(B, delta, phi, v, a, tau)

        # Iterative algorithm to find a new sigma^2
        while abs(B - A) > epsilon:
            C = A + (A - B) * f_A / (f_B - f_A)
            f_C = self._a_func(C, delta, phi, v, a, tau)

            if f_C * f_B < 0:
                A = B
                f_A = f_B
            else:
                f_A /= 2

            B = C
            f_B = f_C
        
        return math.exp(A / 2) # new_sigma

    def _apply_rd_decay(self, current_time: datetime) -> None:
        """
        Applies RD decay based on inactivity.
        The RD increases iteratively for each rating period of inactivity.
        """
        if self.last_played is None:
            return

        # Calculate total days since last activity
        total_days_inactive = (current_time - self.last_played).days

        # Only apply decay if inactive period exceeds the threshold
        if total_days_inactive > self.inactivity_period_days:
            # Number of rating periods of inactivity past the threshold
            # Each rating period is 1 day, so this is just `total_days_inactive - inactivity_period_days`
            num_decay_periods = total_days_inactive - self.inactivity_period_days
            
            # Apply the Glicko-2 RD increase formula for each period
            for _ in range(num_decay_periods):
                self._glicko2_rd = math.sqrt(self._glicko2_rd**2 + self.volatility**2)

    def update_rating(
        self, 
        opponent_data: List[Tuple[float, float, float]],
        current_time: Union[datetime, None] = None
    ) -> None:
        """
        Updates the player's Glicko-2 rating, RD, and volatility.

        Args:
            opponent_data: A list of tuples, where each tuple contains:
                (opponent_rating: float, opponent_rd: float, outcome: float)
                Outcome is 1 for win, 0 for loss, 0.5 for draw.
            current_time: The current datetime. If None, uses datetime.utcnow().
                          Used for RD decay calculation.
        """
        if current_time is None:
            current_time = datetime.utcnow()

        # Step 2: Apply RD decay if player has been inactive
        self._apply_rd_decay(current_time)

        if not opponent_data:
            # If no new games, only RD decay happens. Update public facing values and return.
            self.rating = (_DEFAULT_INITIAL_RATING + self._glicko2_rating / self._q)
            self.rd = self._glicko2_rd / self._q
            self.rd = max(self.rd_floor, min(self.rd, self.rd_ceiling)) # Clamp RD
            self.last_played = current_time
            return

        # Step 3: Calculate v, the variance of the improved rating
        v = self._calculate_v(opponent_data)

        # Step 4: Calculate delta, the estimated improvement in rating
        delta = self._calculate_delta(v, opponent_data)

        # Step 5: Determine new volatility (sigma')
        new_volatility = self._find_new_volatility(delta, v)
        self.volatility = new_volatility

        # Step 6: Update the rating deviation (phi*)
        phi_star = math.sqrt(self._glicko2_rd**2 + new_volatility**2)

        # Step 7: Update the rating and RD
        new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
        new_mu = self._glicko2_rating + new_phi**2 * (delta / v)

        self._glicko2_rating = new_mu
        self._glicko2_rd = new_phi

        # Scale back up for public facing values
        self.rating = (_DEFAULT_INITIAL_RATING + self._glicko2_rating / self._q)
        self.rd = self._glicko2_rd / self._q

        # Ensure RD is within defined bounds
        self.rd = max(self.rd_floor, min(self.rd, self.rd_ceiling))

        self.last_played = current_time

    def get_rating_data(self) -> Tuple[float, float, float]:
        """Returns the current rating, RD, and volatility."""
        return self.rating, self.rd, self.volatility

