from MovementStatisticsGenerator import MovementStatisticsGenerator
from CorrectnessStatisticsGenerator import CorrectnessStatisticsGenerator


generator1 = MovementStatisticsGenerator()
generator1.start()
generator1.plot_seaborn()
generator1.plot_matplotlib()

generator2 = CorrectnessStatisticsGenerator()
generator2.start()


