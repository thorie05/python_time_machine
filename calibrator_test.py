from calibrator import Calibrator

cal = Calibrator(1, 2)

print(cal)
print("\n***\n")

cal.add_calibration([1, 2, 3, 4, 5], [1, 2, 5])

print(cal)
print("\n***\n")

print(cal)
print("\n***\n")

cal.order = -1
 
print(cal)
print("\n***\n")
