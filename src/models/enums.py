import enum


class Domain(str, enum.Enum):
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    NUMBER_THEORY = "number_theory"
    COUNTING = "counting"
    LOGIC = "logic"


class MasteryState(str, enum.Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    LESSON = "lesson"
    PRACTICING = "practicing"
    PROFICIENT = "proficient"
    MASTERED = "mastered"


class ContestFamily(str, enum.Enum):
    MATHCOUNTS = "mathcounts"
    AMC_8 = "amc_8"
    AMC_10 = "amc_10"
    AMC_12 = "amc_12"
    AIME = "aime"
    MU_ALPHA_THETA = "mu_alpha_theta"
    SAT = "sat"
    AP_CALC = "ap_calc"
    AP_LANG = "ap_lang"
    TEXTBOOK = "textbook"


class RoundType(str, enum.Enum):
    SPRINT = "sprint"
    TARGET = "target"
    TEAM = "team"
    COUNTDOWN = "countdown"
    INDIVIDUAL = "individual"
    SECTION = "section"


class CalibrationSource(str, enum.Enum):
    EXPERT = "expert"
    HEURISTIC = "heuristic"
    MODEL = "model"
    STUDENT_DATA = "student_data"
