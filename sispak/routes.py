from flask import render_template, flash, redirect, url_for, session, request, jsonify
from sispak import app, db
from sispak.forms import LoginForm, RegistrationForm, ProfilForm, FormGejala, FormPenyakit
from wtforms import Label
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from sispak.models import User, Gejala, Penyakit, relasi_tabel

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/initial/', methods=['GET', 'POST'])
def initial():
    data_user = User.query.all()
    if len(data_user) > 0:
        return render_template('404.html'), 404

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, type_user=form.user_type.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Akun %s berhasil dibuat!' % (form.username.data))
        return redirect(url_for('login'))
    
    data_user = User.query.all()
    return render_template('register.html', title='INISIASI', form=form, data_pengguna=data_user, pjg=len(data_user))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        session.pop('_flashes', None)
        flash('Login Success')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    data_user = User.query.all()
    return render_template('login.html', title='Log in', form=form, pjg=len(data_user))

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/index/')
@login_required
def index():
    if current_user.type_user == 'admin':
        return redirect(url_for('admin_page'))
    elif current_user.type_user == 'pakar':
        return redirect(url_for('pakar_page'))
    else:
        return redirect(url_for('login'))

@app.route('/index/myprofil/')
@login_required
def my_profil():
    if current_user.type_user == 'admin':
        return redirect(url_for('admin_profil'))
    elif current_user.type_user == 'pakar':
        return redirect(url_for('pakar_profil'))
    else:
        return redirect(url_for('login'))

@app.route('/index/editmyprofil/')
@login_required
def edit_my_profil():
    if current_user.type_user == 'admin':
        return redirect(url_for('admin_edit_profil'))
    elif current_user.type_user == 'pakar':
        return redirect(url_for('pakar_edit_profil'))
    else:
        return redirect(url_for('login'))

# ADMIN
@app.route('/admin/')
@login_required
def admin_page():
    if current_user.type_user != 'admin':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    return render_template('admin.html', title='Admin - Dashboard')

@app.route('/admin/profil/')
@login_required
def admin_profil():
    if current_user.type_user != 'admin':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    search_user = User.query.filter(User.id == current_user.id).first()
    return render_template('profil.html', title='Admin - Profil', edit=False, user=search_user)

@app.route('/admin/profil/edit/', methods=['GET', 'POST'])
@login_required
def admin_edit_profil():
    if current_user.type_user != 'admin':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    search_user = User.query.filter(User.id == current_user.id).first()
    form = ProfilForm()
    if form.validate_on_submit():
        if form.username.data:
            search_user.username = form.username.data
        if form.password.data:
            search_user.set_password(form.password.data)
        db.session.commit()
        flash('Akun %s diupdate!' % (form.username.data))
        return redirect(url_for('admin_profil'))

    form.submit.label = Label(form.submit.id, 'Simpan')
    return render_template('profil.html', title='Admin - Profil', edit=True, user=search_user, form=form)

@app.route('/admin/user/', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.type_user != 'admin':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, type_user=form.user_type.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Akun %s berhasil dibuat!' % (form.username.data))
        return redirect(url_for('register'))
    
    data_user = User.query.all()
    return render_template('register.html', title='Tambah Data Administrator / Pakar', form=form, data_pengguna=data_user, pjg=len(data_user))

@app.route('/admin/user/delete?<id_user>/', methods=['GET', 'POST'])
@login_required
def delete_user(id_user):
    if current_user.type_user != 'admin':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    search_user = User.query.filter(User.id == id_user)
    user = search_user.first()
    if user == current_user:
        flash('Tidak bisa menghapus Akun (%s) anda sendiri!' % (user.username))
        return redirect(url_for('register'))    

    flash('Akun %s telah dihapus!' % (user.username))
    search_user.delete()
    db.session.commit()
    return redirect(url_for('register'))

# @app.route('/admin/botconfig/', methods=['GET', 'POST'])
# @login_required
# def admin_botconfig():
#     if current_user.type_user != 'admin':
#         flash('User tidak memiliki hak akses')
#         return redirect(url_for('index'))

#     botconfig = BotConfig.query.limit(1).all()
#     if len(botconfig) > 0:
#         botconfig = BotConfig.query.filter_by().first()
#     return render_template('botconfig.html', title='Admin - Bot Config', edit=False, botconfig = botconfig)

# @app.route('/admin/botconfig/edit/', methods=['GET', 'POST'])
# @login_required
# def admin_botconfig_edit():
#     if current_user.type_user != 'admin':
#         flash('User tidak memiliki hak akses')
#         return redirect(url_for('index'))

#     botconfig = BotConfig.query.limit(1).all()
#     form = FormBotConfig()
#     if form.validate_on_submit():
#         if len(botconfig) > 0:
#             botconfig = BotConfig.query.filter_by().first()
#             if form.token.data:
#                 botconfig.token = form.token.data
#         else:
#             bot = BotConfig(token=form.token.data)
#             db.session.add(bot)
#         db.session.commit()
#         flash('Bot Config diupdate!')
#         return redirect(url_for('admin_botconfig'))

#     if len(botconfig) > 0:
#         botconfig = BotConfig.query.filter_by().first()
#     return render_template('botconfig.html', title='Admin - Bot Config', edit=True, botconfig = botconfig, form=form)

# PAKAR
@app.route('/pakar/')
@login_required
def pakar_page():
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))
    
    data_penyakit = Penyakit.query.order_by(Penyakit.id).all()
    data_gejala = Gejala.query.order_by(Gejala.id).all()
    
    return render_template(
        'pakar.html', 
        title='Pakar - Dashboard', 
        jml_penyakit=len(data_penyakit), 
        penyakit=data_penyakit, 
        gejala=data_gejala,)

@app.route('/pakar/profil/')
@login_required
def pakar_profil():
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    search_user = User.query.filter(User.id == current_user.id).first()
    return render_template('profil.html', title='Pakar - Profil', edit=False, user=search_user)

@app.route('/pakar/profil/edit/', methods=['GET', 'POST'])
@login_required
def pakar_edit_profil():
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    search_user = User.query.filter(User.id == current_user.id).first()
    form = ProfilForm()
    if form.validate_on_submit():
        if form.username.data:
            search_user.username = form.username.data
        if form.password.data:
            search_user.set_password(form.password.data)
        db.session.commit()
        flash('Akun %s diupdate!' % (form.username.data))
        return redirect(url_for('pakar_profil'))

    form.submit.label = Label(form.submit.id, 'Simpan')
    return render_template('profil.html', title='Pakar - Profil', edit=True, user=search_user, form=form)

@app.route('/pakar/gejala/', methods=['GET', 'POST'])
@login_required
def pakar_gejala():
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    form = FormGejala()
    if form.validate_on_submit():
        gejala = Gejala(kode=form.kode.data, gejala=form.gejala.data, deskripsi=form.deskripsi.data)
        db.session.add(gejala)
        db.session.commit()
        flash('Gejala %s - %s berhasil disimpan!' % (form.kode.data, form.gejala.data))
        return redirect(url_for('pakar_gejala'))

    data_gejala = Gejala.query.order_by(Gejala.id).all()
    gejala_last = Gejala.query.order_by(Gejala.id.desc()).first()
    if gejala_last != None:
        last_id = gejala_last.id
    else:
        last_id = 0
    kode = "G{0:03}".format(last_id + 1)
    return render_template('pakar_gejala.html', title='Pakar - Data Gejala', form=form, kode=kode, gejala=data_gejala)

@app.route('/pakar/gejala/view?<id_gejala>&<editable>/', methods=['GET', 'POST'])
@login_required
def pakar_gejala_view(id_gejala, editable):
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    form = FormGejala()
    if form.validate_on_submit():
        data_gejala = Gejala.query.get(id_gejala)
        data_gejala.gejala = form.gejala.data
        data_gejala.deskripsi = form.deskripsi.data
        db.session.commit()

        flash('Gejala %s - %s berhasil diupdate!' % (form.kode.data, form.gejala.data))
        return redirect(url_for('pakar_gejala_view', id_gejala = id_gejala, editable=False))

    data_gejala = Gejala.query.get(id_gejala)
    form.deskripsi.data = data_gejala.deskripsi
    return render_template('pakar_gejala_view.html', title='Pakar - Data Gejala', form=form, edit=editable, gejala=data_gejala)

@app.route('/pakar/gejala/delete?<id_gejala>/', methods=['GET', 'POST'])
@login_required
def pakar_gejala_delete(id_gejala):
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    gejala = Gejala.query.filter(Gejala.id == id_gejala)
    data_gejala = gejala.first()
    if len(data_gejala.penyakit) > 0:
        flash('Gejala %s - %s tidak bisa dihapus, karena memiliki relasi dengan data penyakit!' % (data_gejala.kode, data_gejala.gejala))
        return redirect(url_for('pakar_gejala'))

    data_gejala = gejala.first()
    flash('Gejala %s - %s telah dihapus!' % (data_gejala.kode, data_gejala.gejala))
    gejala.delete()
    db.session.commit()
    return redirect(url_for('pakar_gejala'))

@app.route('/pakar/penyakit/', methods=['GET', 'POST'])
@login_required
def pakar_penyakit():
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    form = FormPenyakit()
    gejala_list = Gejala.query.order_by(Gejala.id).all()
    my_choices = [(int(x.id), x.kode + " - " + x.gejala) for x in gejala_list]
    form.gejala.choices = my_choices
    if form.validate_on_submit():
        penyakit = Penyakit(kode=form.kode.data, penyakit=form.penyakit.data, deskripsi=form.deskripsi.data, penanganan=form.penanganan.data)
        db.session.add(penyakit)
        db.session.commit()
        
        daftar_gejala = form.gejala.data
        for i in daftar_gejala:
            gejala = Gejala.query.filter(Gejala.id == int(i)).one()
            penyakit.gejala.append(gejala)
            db.session.commit()

        flash('Penyakit %s - %s berhasil disimpan!' % (form.kode.data, form.gejala.data))
        return redirect(url_for('pakar_penyakit'))

    data_penyakit = Penyakit.query.order_by(Penyakit.id).all()
    penyakit_last = Penyakit.query.order_by(Penyakit.id.desc()).first()
    if penyakit_last != None:
        last_id = penyakit_last.id
    else:
        last_id = 0
    kode = "P{0:03}".format(last_id + 1)
    return render_template('pakar_penyakit.html', title='Pakar - Data Penyakit', form=form, kode=kode, penyakit=data_penyakit)

@app.route('/pakar/penyakit/view?<id_penyakit>&<editable>/', methods=['GET', 'POST'])
@login_required
def pakar_penyakit_view(id_penyakit, editable):
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    form = FormPenyakit()
    gejala_list = Gejala.query.order_by(Gejala.id).all()
    my_choices = [(int(x.id), x.kode + " - " + x.gejala) for x in gejala_list]
    form.gejala.choices = my_choices
    if form.validate_on_submit():
        data_penyakit = Penyakit.query.get(id_penyakit)
        data_penyakit.penyakit = form.penyakit.data
        data_penyakit.deskripsi = form.deskripsi.data
        data_penyakit.penanganan = form.penanganan.data
        data_penyakit.gejala.clear()
        db.session.commit()
        
        daftar_gejala = form.gejala.data
        for i in daftar_gejala:
            gejala = Gejala.query.get(i)
            data_penyakit.gejala.append(gejala)
            db.session.commit()

        flash('Penyakit %s - %s berhasil diupdate!' % (form.kode.data, form.penyakit.data))
        return redirect(url_for('pakar_penyakit_view', id_penyakit = id_penyakit, editable=False))

    data_penyakit = Penyakit.query.get(id_penyakit)
    form.deskripsi.data = data_penyakit.deskripsi
    form.penanganan.data = data_penyakit.penanganan
    form.gejala.data = [i.id for i in data_penyakit.gejala]
    return render_template('pakar_penyakit_view.html', title='Pakar - Data Penyakit', form=form, edit=editable, penyakit=data_penyakit)
    
@app.route('/pakar/penyakit/delete?<id_penyakit>/', methods=['GET', 'POST'])
@login_required
def pakar_penyakit_delete(id_penyakit):
    if current_user.type_user != 'pakar':
        flash('User tidak memiliki hak akses')
        return redirect(url_for('index'))

    penyakit = Penyakit.query.filter(Penyakit.id == id_penyakit)
    data_penyakit = penyakit.first()
    if len(data_penyakit.gejala) > 0:
        flash('Gejala %s - %s tidak bisa dihapus, karena masih memiliki relasi dengan data gejala!' % (data_penyakit.kode, data_penyakit.penyakit))
        return redirect(url_for('pakar_penyakit'))

    flash('Penyakit %s - %s telah dihapus!' % (data_penyakit.kode, data_penyakit.penyakit))
    penyakit.delete()
    db.session.commit()
    return redirect(url_for('pakar_penyakit'))

def compute_next(kamus):
    mentah_penyakit = kamus['penyakit']
    mentah_gejala = kamus['gejala']
    gejala = Gejala.query.filter(Gejala.id.in_(mentah_gejala)).all()
    panjang_penyakit = len(mentah_penyakit)
    g_max = 0
    item = 0
    for i in gejala:
        c = Gejala.query.filter(Gejala.id == i.id).one()
        print (c.gejala)
        print (len(c.penyakit))
        if item == 0:
            a = Gejala.query.filter(Gejala.id == i.id).one()
            if len(a.penyakit) == panjang_penyakit:
                continue
            g_max = i.id
            item = item + 1
        else:
            a = Gejala.query.filter(Gejala.id == g_max).one()
            a_penyakit = [ i.id for i in a.penyakit]
            count_a = 0
            for j in mentah_penyakit:
                if j in a_penyakit:
                    count_a = count_a + 1
            b = Gejala.query.filter(Gejala.id == i.id).one()
            b_penyakit = [ i.id for i in b.penyakit]
            count_b = 0
            for j in mentah_penyakit:
                if j in b_penyakit:
                    count_b = count_b + 1

            if count_b < panjang_penyakit:
                if count_a < count_b:
                    g_max = b.id
            item = item + 1
        
    penyakit_yes = []
    penyakit_no = []
    
    next_gejala = Gejala.query.filter(Gejala.id == g_max).one()
    penyakit_in_next_gejala = [ i.id for i in next_gejala.penyakit ]
    for i in mentah_penyakit:
        if i in penyakit_in_next_gejala:
            penyakit_yes.append(i)
        else:
            penyakit_no.append(i)
            
    mentah_gejala.remove(g_max)
    sisa_gejala = Gejala.query.filter(Gejala.id.in_(mentah_gejala)).all()
    
    gejala_yes = []
    gejala_no = []
	
    for i in sisa_gejala:
        for j in i.penyakit:
            if j in next_gejala.penyakit:
                gejala_yes.append(i.id)
                break

    for i in sisa_gejala:
        for j in i.penyakit:
            if j not in next_gejala.penyakit:
                gejala_no.append(i.id)
                break

    pertanyaan = next_gejala.gejala
    message = "belum"
    deskripsi = "belum"
    solusi = "belum"
    if len(mentah_penyakit) == 1:
        penyakit = Penyakit.query.filter(Penyakit.id == mentah_penyakit[0]).one()
        pertanyaan = penyakit.penyakit
        message = "sudah"
        deskripsi = penyakit.deskripsi
        solusi = penyakit.penanganan
    results = {
		'penyakit_yes' : penyakit_yes,
		'penyakit_no' : penyakit_no,
		'gejala_yes' : gejala_yes,
		'gejala_no' : gejala_no,
		'pertanyaan' : pertanyaan,
		'message' : message,
        'deskripsi' : deskripsi,
        'solusi' : solusi,
	}
    return results

@app.route('/diagnosa', methods=['GET','POST'])
def diagnosa():
	return render_template('tes_diagnosa.html',)

@app.route('/start_diagnosa', methods=['POST', 'GET'])
def start_diagnosa(): 
    daftar_penyakit = Penyakit.query.all()
    daftar_gejala = Gejala.query.all()
    penyakit= []
    gejala = []
    for i in daftar_gejala:
        gejala.append(i.id)
    for i in daftar_penyakit:
        penyakit.append(i.id)
	
    print (penyakit)
    print (gejala)
    kamus = {
		'penyakit': penyakit,
		'gejala':gejala,
	}
    results = compute_next(kamus)
    print ("RESUTL")
    print (results)
    return jsonify(results)

@app.route('/process_ya', methods=['POST', 'GET'])
def proses_ya():
    hasil = {}
    mentah_penyakit = []
    mentah_gejala = []
    if request.method == "POST":
        hasil = request.get_json()
        mentah_penyakit = [ int(i) for i in hasil['penyakit'] ]
        mentah_gejala = [ int(i) for i in hasil['gejala'] ]
    kamus = {
		'penyakit': mentah_penyakit,
		'gejala':mentah_gejala,
	}
    results = compute_next(kamus)
    return jsonify(results)