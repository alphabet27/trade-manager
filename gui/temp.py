class timestamp:
	def __init__(self, hours, mins, secs):
		self.hours = hours
		self.mins = mins
		self.secs = secs

	def __str__(self):
		return str(self.hours).rjust(2, "0") + ":" + str(self.mins).rjust(2, "0") + ":" + str(self.secs).rjust(2, "0")

t1 = timestamp(0, 3, 0)
t2 = timestamp(1, 5, 0)

print(t1)
print(t1.mins)
print(t1.secs)
