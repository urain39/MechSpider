class Group(list):
  VISIT_METHOD_OPEN = object()
  VISIT_METHOD_FOLLOW = object()

  def __init__(self):
    self.method = self.VISIT_METHOD_OPEN

    super().__init__()
