from django.template.loader import render_to_string


class WidgetRendererService:

    template_name: str

    type: str

    def render(self, request):
        context = self.get_context_data()
        return render_to_string(self.template_name, context, request)
