# Practical 6 - Keyframe Animation

## Exercise 1 - Interpolator Class

We need to complete the function `value(self, time)` from the class `KeyFrames`, such that it returns the interpolated value, given a range of key-value pairs and a key (`time`) whose corresponding value is unknown (aka the interpolated value to be found out).

The key-value pairs are obtained in the constructor of the KeyFrames class:

```py
self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
```

where `times` is a list of keys, and `values` is its list of corresponding values. Each entry of `times` is like the timestamp of the trajectory, and `values` is the corresponding coordinate (could be in x/y/z) at that timestamp.

* Step 1: We first ensure the input key (`time`) is within the boundary keyframe:

```py
# 1. ensure time is within bounds else return boundary keyframe
if time <= self.times[0]: 
    return self.values[0]
elif time >= self.times[len(self.times) - 1]:
    return self.values[len(self.times) - 1]
```
All we are doing is ensuring that `time` is within the first and last timestamp. If it's not, then we return the boundary value itself.

* Step 2: We look for the timestamp (from `times`) which is closest to our `time` variable:

```py
# 2. search for closest index entry in self.times, using bisect_left function
index_closest = bisect_left(self.times, time)
```

We simply make use of an in-built function `bisect_left(a, b)` from the `bisect` library to find us the index of the nearest timestamp entry (nearest *left-side* of our `time`)

* Step 3: We then calculate a fraction and using it, we get the interpolated value by passing a, b (aka the values corresponding to timestamp) and f to the interpolate function:


```py
# 3. using the retrieved index, interpolate between the two neighboring values
# in self.values, using the initially stored self.interpolate function
f = (time - self.times[index_closest - 1]) / (self.times[index_closest] - self.times[index_closest - 1])

interpolated_val = self.interpolate(self.values[index_closest], self.values[index_closest - 1], f)
```

__Example__

```
lerp = a + f * (b - a)
= a + f*b - f*a
= a * (1 - f) + b*f

0:1, 3:7, 6: 20
1.5: ?

f = (1.5 - 0) / (3 - 0) = 0.5
lerp = a + f * (b - a)
= 1 + 0.5 * (7 - 1)
= 1 + 6/2
= 4