from pprint import pformat

title_bar = lambda title='', rep=64: f' {title} '.rjust(1+rep//2 + len(title)//2, '=').ljust(rep, '=')
pf = lambda *args, **kwargs: pformat(*args, **kwargs, sort_dicts=False)

box = lambda text, title='', prefix='', rep=64: f'\n{rep*"=" if not title else title_bar(title, rep)}\n{prefix}{text}\n{rep*"="}\n'
fox = lambda text, title='', prefix='', rep=64: f'\n{rep*"=" if not title else title_bar(title, rep)}\n{prefix}{pf(text)}\n{rep*"="}\n'

def catch(func, *args, **kwargs):
    '''https://stackoverflow.com/a/8915613/2571805'''
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return e

