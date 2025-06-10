class coords:
  def __init__(self, w): 

    self.w = []
    self.w.append(w[0] * 5) 
    self.w.append(w[1] * 5) 
    self.w.append(w[2] * 5) 
    self.w.append(w[3] * 5) 

    self.x = w[0] + 0.5 * 3**0.5 * w[1] + 0.5 * w[2]; 
    self.y = 0.5 * w[1] + 0.5 * 3**0.5 * w[2] + w[3]; 
  
  def translate(self, wc):
    c = [(w_ + wc_)/5 for w_, wc_ in zip(self.w, wc.w)]

    return coords(c) 
  
  def scale(self, k):
    c = [(w_ * k)/5 for w_ in self.w]

    return coords(c) 

  def __str__(self):
      return f"{self.x}, {self.y}" 

class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class circle:
    def __init__(self, c, r):
        self.c = c
        self.r = r


