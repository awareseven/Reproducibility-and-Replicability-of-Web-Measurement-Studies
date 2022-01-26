import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import pandas as pd
import os

# Read the data
path = os.path.join(os.getcwd(), "results")
df = pd.read_csv(os.path.join(path, "tracker_AND_cookies.csv"))

x = df["day"]
y1 = df["total_tracker"]
y2 = df["tracker_distinct"]
y3 = df["is_session"]

# Some styling stuff
fig, ax = plt.subplots(1, figsize=(7, 4))
legend_properties = {'weight': 'bold', 'size': 9}
font = font_manager.FontProperties(family='sans-serif',
                                   weight='bold',
                                   style='normal',
                                   size=14)
plt.legend(loc='best', frameon=False, prop=font)
plt.xticks(weight='bold', fontname='sans-serif', size=14)
plt.yticks(weight='bold', fontname='sans-serif', size=14)

plt.xlabel("Measurement point", weight='bold', fontname='sans-serif', size=14)


# Add first y-axis (Number of tracking requests)
ax.plot(x, y1, color="#999999", label="Number of tracking requests", marker='o', linestyle='dashed')
ax.set_ylabel('Number of tracking requests')
ax.legend(loc=2, prop=legend_properties)
plt.ylabel("Number of tracking requests", weight='bold', fontname='sans-serif', size=14)

# Add second y-axis
ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
ax2.plot(x, y2, color="#555555", label="Number of distinct trackers", marker='x', linestyle='solid')
ax2.set_ylabel('Number of distinct trackers')
ax2.set_ylim(3500, 4200)
ax2.legend(loc=1, prop=legend_properties)
plt.ylabel("Number of distinct trackers", weight='bold', fontname='sans-serif', size=14)
plt.yticks(weight='bold', fontname='sans-serif')

# Save plot to disc
plt.grid(False)
#plt.show()
plt.savefig(path + "/04_long_term_tracker_cookies.pdf", dpi=600,
            transparent=False,  bbox_inches='tight', format="pdf")

# Simple min / max calculations
max_value = y1.max()
min_value = y1.min()
max_day = y1.index[df['total_tracker'] == max_value].tolist()
min_day = y1.index[df['total_tracker'] == min_value].tolist()
print("Max at: ", max_day, "max value: ", max_value)
print("Min at: ", min_day, "min value: ", min_value)
print("std:", y1.std())
