from . import v1_school, v2_fitness, v3_gymnastics

VARIANTS = {
    1: v1_school.build,
    2: v2_fitness.build,
    3: v3_gymnastics.build,
}
