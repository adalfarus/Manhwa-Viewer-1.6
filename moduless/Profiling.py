import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... your code ...

profiler.disable()

# Save profile results to a file
profiler.dump_stats('profile_results.prof')

# Load profile results from file
p = pstats.Stats('profile_results.prof')

# Strip directory names from file paths in the profile output
p.strip_dirs()

# Sort the profile results by cumulative time spent in functions
p.sort_stats('cumulative')

# Print the top 10 functions that took the most time
p.print_stats(10)

# Alternatively, you can filter the results to include only functions
# that took more than a certain amount of time, for example, 0.1 seconds:
p.fcn_list = [key for key, value in p.stats.items() if value[3] > 0.1]  # value[3] is the cumulative time
p.print_stats()
