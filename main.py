import urllib
from flask import Flask, render_template, request
import configparser as cf
import users

app = Flask(__name__)


@app.route('/', methods=['GET'])
def login():
    conferenses = cf.ConfigParser()
    conferenses.read('conferences.ini')
    to_html = {}
    for conf in conferenses:
        if conf != 'DEFAULT':
            data = {conf:
                        {'name': f'{conferenses[conf]["name"].encode("1251").decode("UTF-8")}',
                         'about': f'{conferenses[conf]["about"].encode("1251").decode("UTF-8")}',
                         'date': f'{conferenses[conf]["date"].encode("1251").decode("UTF-8")}',
                         'lector': f'{conferenses[conf]["lector"].encode("1251").decode("UTF-8")}'}
                    }
            to_html.update(data)

    return render_template('main.html', context=to_html)


@app.route('/', methods=['POST'])
def open_conference():
    req = request.get_data()
    data = urllib.parse.unquote(req)
    action = data.split('=')[-1]
    if action in 'Регистрация':
        confid = data.split('=')[0].replace('+', ' ')
        context = {}
        context['confid'] = confid
        return render_template('regtoconf.html', context=context)
    elif action in 'Отправить':
        to_csv = data.replace('fio=', '').replace('phone=', '').replace('+', ' ').replace('=Отправить', '').split('&')
        with open("regdata.csv", "a", encoding='UTF-8') as file:
            file.write(f"{to_csv[0]};{to_csv[1]};{to_csv[2]}\n")
        context = 'Спасибо! Ваша заявка успешно принята, мы свяжемя с Вами в ближайшее время!'
        return render_template('succsess.html', context=context)


@app.route('/authorization', methods=['GET'])
def auth():
    return render_template('authorization.html')


@app.route('/authorization', methods=['POST'])
def auth_data():
    req = request.get_data()
    data = urllib.parse.unquote(req)
    authorization = data.replace('ID=', '').replace('name=', '').replace('action=', '').split('&')
    if authorization[-1] == 'Войти':
        try:
            stored_pass = getattr(users, authorization[0])
            if authorization[1] == stored_pass:
                return render_template('admin_area.html')
            else:
                return render_template('authorization.html')
        except:
            return render_template('authorization.html')
    elif authorization[-1] == 'Перейти':
        if authorization[0] == 'create_conf':
            return render_template('createconf.html')
        elif authorization[0] == 'remove_conf':
            return remove()
    elif authorization[-1] == 'Создать':
        return createconftofile()
    elif authorization[-1] == 'Удалить':
        return removefromfile()


def removefromfile():
    req = request.get_data()
    data = urllib.parse.unquote(req)
    confs = data.replace('=on', '').replace('&Remove=Удалить!', '').split('&')
    config = cf.ConfigParser()
    config.read('conferences.ini')
    for conf in confs:
        config.remove_section(conf)
    with open("conferences.ini", "w") as f:
        config.write(f)
    context = 'Конференции успешно удалены!'
    return render_template('succsess.html', context=context)


def createconftofile():
    req = request.get_data()
    data = urllib.parse.unquote(req)
    conf = data.replace('+', ' ').replace('ID=', '').replace('name=', ' ').replace('about=', ' ').replace('date=',
                                                                                                          ' ').replace(
        'lector=', ' ').split('&')
    with open("conferences.ini", "a", encoding='UTF-8') as file:
        file.write(f"[{conf[0]}]\n"
                   f"name = {conf[1]}\n"
                   f"about = {conf[2]}\n"
                   f"date = {conf[3]}\n"
                   f"lector = "
                   f"{conf[4]}\n")
    context = 'Конференция создана успешно!'
    return render_template('succsess.html', context=context)


def remove():
    conferences = cf.ConfigParser()
    conferences.read('conferences.ini')
    to_html = []
    for conf in conferences:
        if conf != 'DEFAULT':
            to_html.append(conf)
    return render_template('remove_conf.html', context=to_html)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
