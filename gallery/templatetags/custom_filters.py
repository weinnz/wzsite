from django import template

register = template.Library()
@register.filter
def change_date_format_1(date):
   _, y = date.split(" ")
   m, d = _.split("/")
   return f"{y} {int(m):02d}/{int(d):02d}"

@register.filter
def change_date_format_2(date):
   _, y = date.split(" ")
   m, d = _.split("/")
   return f"{y}-{int(m):02d}-{int(d):02d}"