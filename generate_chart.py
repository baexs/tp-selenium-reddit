import matplotlib.pyplot as plt
from datetime import datetime, timedelta

today = datetime.now()
dates = [(today - timedelta(days=2)).strftime("%Y-%m-%d"), 
         (today - timedelta(days=1)).strftime("%Y-%m-%d"), 
         today.strftime("%Y-%m-%d")]

ok = [2, 1, 3]
ko = [1, 2, 0]

plt.plot(dates, ok, label="Tests OK", marker="o", color="green")
plt.plot(dates, ko, label="Tests KO", marker="x", color="red")
plt.xlabel("Date")
plt.ylabel("Nombre de tests")
plt.title("Évolution des résultats des tests")
plt.legend()
plt.savefig("test_results.png")
