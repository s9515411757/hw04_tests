from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['author_title'] = 'Привет, я автор'
        context['author_text'] = ('Тут я размещу информацию о себе, используя '
                                  'свои умения верстать. Картинки, блоки, '
                                  'элементы бустрап. А может быть, просто '
                                  'напишу несколько абзацев текста.')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['tech_title'] = 'Очень простая страница'
        context['tech_text'] = 'Текст страницы "Технологии"'
        context['tech_technologies_list'] = ('Python', 'Django')

        return context
