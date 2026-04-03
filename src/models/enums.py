import enum


class Domain(str, enum.Enum):
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    NUMBER_THEORY = "number_theory"
    COUNTING = "counting"
    LOGIC = "logic"
    MATH = "math"
    QUANTITATIVE_REASONING = "quantitative_reasoning"
    SCIENCE = "science"
    READING = "reading"


class MasteryState(str, enum.Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    LESSON = "lesson"
    PRACTICING = "practicing"
    PROFICIENT = "proficient"
    MASTERED = "mastered"


class ContestFamily(str, enum.Enum):
    MATHCOUNTS = "mathcounts"
    AMC_8 = "amc8"
    AMC_10 = "amc10"
    AMC_12 = "amc12"
    AMC = "amc"
    AMC_AIME = "amc_aime"
    AIME = "aime"
    HMMT = "hmmt"
    FAMAT = "famat"
    SAT = "sat"
    GRE_GMAT = "gre_gmat"
    LSAT = "lsat"
    MMLU = "mmlu"
    OLYMPIAD = "olympiad"
    CHINESE_K12 = "chinese_k12"
    SYNTHETIC_MATH = "synthetic_math"
    SYNTHETIC_AMC = "synthetic_amc"
    ORCA_MATH = "orca_math"
    GSM8K = "gsm8k"
    AOPS_FORUM = "aops_forum"
    MATH_COMPETITION = "math_competition"
    ARC_SCIENCE = "arc_science"
    OPENBOOKQA = "openbookqa"
    LOGIC = "logic"
    MATH_PREALGEBRA = "math_prealgebra"
    OTHER = "other"


class AnswerType(str, enum.Enum):
    NUMERIC = "numeric"
    MULTIPLE_CHOICE = "multiple_choice"
    EXPRESSION = "expression"
    FREE_RESPONSE = "free_response"
    OPEN_ENDED = "open_ended"
    FRACTION = "fraction"
    WORD = "word"
    UNKNOWN = "unknown"


class GradeBand(str, enum.Enum):
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "ms"
    HIGH_SCHOOL = "hs"
    AP_HONORS = "ap"
    COLLEGE = "col"
    GRADUATE = "grad"
    COMPETITION = "competition"


class TextFormat(str, enum.Enum):
    PLAIN = "plain"
    LATEX = "latex"
    HTML = "html"
    MARKDOWN = "markdown"


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
