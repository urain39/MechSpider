class Group(list):
  VISIT_METHOD_OPEN = object()
  VISIT_METHOD_FOLLOW = object()

  def __init__(self, *args, **kwargs):
    self.method = self.VISIT_METHOD_FOLLOW

    super().__init__(*args, **kwargs)
