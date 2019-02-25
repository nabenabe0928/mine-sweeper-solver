import copy
import numpy as np

def combination(n, r):
  c = 1.0
  mul = [k for k in range(n, n - r, -1)]

  for i, m in enumerate(mul):
    c *= float(m) / float(i + 1)

  return c


class probability():
  def __init__(
	self, 
	player, 
	flag):

    self.player = player
    self.flag = copy.deepcopy(flag)
    self.flag_sum = sum([f.count(True) for f in flag])
    self.B = self.player.B
    self.W = player.width
    self.H = player.height
    self.countL = 0
    self.count = 0
    self.up_to_here = -1
    self.target = self.init_target()
    self.n_none = self.target[1].count(None)
    self.L = self.W * self.H - self.flag_sum - len(self.target[0]) - self.count_open()

  def count_open(self):
    n_open = 0

    for w in range(self.W):
      for h in range(self.H):
        if self.player.GetCellInfo(w, h) >= 0:
          n_open += 1
    return n_open


  def init_target(self):
    target = [[],[],[]]

    for w in range(self.W):
      for h in range(self.H):
        if self.player.GetCellInfo(w, h) == -1 and not self.flag[w][h] and not self.is_land(w, h):
          target[0].append(self.position_to_num(w, h))
          target[1].append(None)
          target[2].append(0)

    return target

  def is_land(self, x, y):
    ard = self.player.around(x, y)

    for a in ard:
      if self.player.GetCellInfo(a[0], a[1]) != -1:
        return False
    
    return True

  def GetFlag(self):
    for w in range(self.W):
      for h in range(self.H):
        if self.player.GetCellInfo(w, h) != -1:
          count = 0
          around = self.player.around(w, h)
          
          for a in around:
            num = self.position_to_num(a[0], a[1])
            
            if num in self.target[0]:
              idx = self.target[0].index(num)
							
              if self.target[1][idx] != 0:
                count += 1
            
            else:
              if self.player.GetCellInfo(a[0], a[1]) == -1:
                count += 1
					
          if count == self.player.GetCellInfo(w, h):
            for a in around:
              num = self.position_to_num(a[0], a[1])
              
              if num in self.target[0]:
                idx = self.target[0].index(num)
							
                if self.target[1][idx] != 0 and self.target[1][idx] != 2:
                  self.target[1][idx] = 1
		
          elif count < self.player.GetCellInfo(w, h):
            self.renew_target()
						
  def OpenSafe(self):
    for w in range(self.W):
      for h in range(self.H):
        if self.player.GetCellInfo(w, h) != -1:
          count = 0
          around = self.player.around(w, h)
		
          for a in around:
            num = self.position_to_num(a[0], a[1])

            if num in self.target[0]:
              idx = self.target[0].index(num)
							
              if self.target[1][idx] == 1 or self.target[1][idx] == 2:
                count += 1
		
            else:
              if self.flag[a[0]][a[1]]:
                count += 1

          if count == self.player.GetCellInfo(w, h):
            for a in around:
              num = self.position_to_num(a[0], a[1])
	
              if num in self.target[0]:
                idx = self.target[0].index(num)
							
                if self.target[1][idx] != 1 and self.target[1][idx] != 2:
                  self.target[1][idx] = 0
		
          elif count > self.player.GetCellInfo(w, h):
            self.renew_target()
	
  def count_patterns(self):
    left_B = self.B - self.flag_sum - self.target[1].count(1) - self.target[1].count(2)
    patterns = combination(self.L, left_B)
    self.countL += combination(self.L - 1, left_B - 1)
    self.count += patterns
		
    for i in range(len(self.target[1])):
      if self.target[1][i] == 1 or self.target[1][i] == 2:
        self.target[2][i] += patterns

  def new_assumption(self):
    for i in range(len(self.target[1])):
      if self.target[1][i] == None:
        self.target[1][i] = 2

        return None


  def renew_target(self):

    for i in range(len(self.target[1]) - 1, self.up_to_here, -1):
      if self.target[1][i] != 2:
        self.target[1][i] = None
      else:
        self.target[1][i] = 0
        if not 2 in self.target[1][:i]:
          self.up_to_here = i
	
        self.new_assumption()
        return None

  def cannot_open(self):
    n_none = self.target[1].count(None)
		
    if n_none == self.n_none:
      return True

    else:
      self.n_none = n_none
      return False

  def position_to_num(self, x, y):
    return x + y * self.W

  def searching(self):
    t = 0
    while 2 in self.target[1] or None in self.target[1]:
      t += 1
      if t % 100 == 0:
        print("{}: {}".format(t, self.up_to_here))

      self.GetFlag()
      self.OpenSafe()
	
      if self.cannot_open(): 
        if self.n_none != 0:
          self.new_assumption()
        else:
          self.count_patterns()
          self.renew_target()

    if self.count != 0:
      self.target[2] = np.asarray(self.target[2]) / self.count

      if self.L != 0:
        self.countL /= self.count
      else:
        self.countL = 1.0

    return self.target, self.countL
