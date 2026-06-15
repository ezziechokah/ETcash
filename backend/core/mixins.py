class CompanyScopedMixin:
    def get_company(self):
        return self.request.user.profile.company

    def get_queryset(self):
        return super().get_queryset().filter(company=self.get_company())

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())
