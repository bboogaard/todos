from haystack.forms import ModelSearchForm as HaystackSearchForm


class SearchForm(HaystackSearchForm):

    def search(self):
        sqs = super().search()
        sqs = sqs.filter(include_in_search=True)
        return sqs
