from datetime import datetime
from distutils import archive_util
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import os
import smtplib
import time
from typing import Callable
import jinja2
import pdfkit
from flask import send_file
from werkzeug.utils import secure_filename
from flask import redirect, render_template, request, send_file, session, url_for, flash

# init_views inicializa la clase de las vistas
# app es un objeto flask creado en app.py (en app.py: app = Flask(__name__)
# db_access es el objeto que devuelve init_db para gestionar la base de datos (en app.py: db_access = init_db(app))
# ambos pasan como parámetros a init_views

# def validate_password(password: str, hashed_password: str) -> bool:
# return hash_password(password) == hashed_password

# ------------------FUNCION DE HASH DE LA PASSWORD-------------------------


def hash_password(password: str) -> str:
    salt = "mysecretsalt"  # puedes usar un valor diferente aquí
    return hashlib.sha256((password + salt).encode()).hexdigest()
# ----------------------------------------------------------------------------


def init_views(app, db_access: dict[str, Callable]):
    # definición de las acciones a realizar para lanzar cada vista
    # nótese que el código de "/" no pregunta si se ha hecho una petición, así que deberá ejecutarse al inicializar
    # en el caso de los demás tienen sentencias IF para que el código se ejecute solo si haya una petición

    # ------------------VIEW DE LOGIN-------------------------
    # --- Aquí controlo si el usuario que netra es admin o no para así mostrar una serie de cosas u otras
    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        if request.method == "POST":
            find_login = db_access["find_login"]
            find_admin = db_access["find_admin"]
            usuario = request.form["usuario"]
            contrasena = hash_password(request.form["contrasena"])

            if find_admin(usuario, contrasena):
                # El inicio de sesión es exitoso
                session['usuario'] = usuario
                return redirect(url_for('inicio'))
            elif find_login(usuario, contrasena):
                # El inicio de sesión es exitoso
                session['usuario'] = usuario
                return redirect(url_for('toldo_user'))
            else:
                error_sesion = "Error de inicio de sesion"
                flash(error_sesion)
                return render_template("login.html")

    # ------------------Cerrar Sesion------------------------

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.clear()
        return render_template("login.html")

    # ------------------VIEW DE Inicio-------------------------

    @app.route("/inicio", methods=["GET", "POST"])
    def inicio():

        # Verificar si el usuario ha iniciado sesión
        if 'usuario' in session:
            usuario = session['usuario']
            usu = usuario
            return render_template("index.html", usu=usu)
        # Si el usuario ha iniciado sesión, mostrar la vista de inicio
        else:
            return "No tiene permisos para acceder"

    @app.route("/inicio_usu", methods=["GET", "POST"])
    def inicio_usu():

        # Verificar si el usuario ha iniciado sesión
        if 'usuario' in session:
            usuario = session['usuario']
            usu = usuario
            return render_template("user/index_usuario.html", usu=usu)
        # Si el usuario ha iniciado sesión, mostrar la vista de inicio
        else:
            return "No tiene permisos para acceder"

    # ------------------VIEW DE REGISTRO-------------------------

    @app.route("/create_usuario", methods=["GET", "POST"])
    def create_usuario():
        if request.method == "GET":
            return render_template("registro.html")

        if request.method == "POST":
            create_usuario = db_access["create_usuario"]
            contrasena_hash = hash_password(request.form["contrasena"])
            create_usuario(
                usuario=request.form["usuario"],
                correo=request.form["correo"],
                contrasena=contrasena_hash,
                rol=""
            )
            return redirect("/")

    # ------------------VIEW DE Toldos ADMIN-------------------------

    @app.route("/toldo", methods=["GET", "POST"])
    def toldo():

        list_toldo = db_access["list_toldos"]
        toldos = list_toldo()
        usuario = session['usuario']
        usu = usuario
        return render_template("toldos.html", toldos=toldos, usu=usu)

    @app.route("/delete_toldo/<int:Toldo_id>", methods=["GET", "POST"])
    def delete_toldo(Toldo_id: int):
        if request.method == "GET":
            read_toldo = db_access["read_toldo"]
            toldo = read_toldo(Toldo_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("delete_toldo.html", toldo=toldo, usu=usu)

        if request.method == "POST":
            delete_toldo = db_access["delete_toldo"]
            delete_toldo(
                Toldo_id=Toldo_id
            )
            return redirect("/toldo")

    @app.route("/create_toldo", methods=["GET", "POST"])
    def create_toldo():
        if request.method == "GET":
            list_toldo = db_access["list_toldos"]
            toldos = list_toldo()
            usuario = session['usuario']
            usu = usuario
            return render_template("create_toldo.html", toldos=toldos, usu=usu)

        if request.method == "POST":
            create_toldo = db_access["create_toldo"]
            create_toldo(
                modelo=request.form["modelo"],
                tipo=request.form["tipo"],
                dimensiones=request.form["dimensiones"],
                imagen=request.form["imagen"]
            )
            return redirect("/toldo")

    @app.route("/update_toldo/<int:Toldo_id>", methods=["GET", "POST"])
    def updtae_toldo(Toldo_id: int):
        if request.method == "GET":
            read_toldo = db_access["read_toldo"]
            toldo = read_toldo(Toldo_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("update_toldo.html", toldo=toldo, usu=usu)

        if request.method == "POST":
            update_toldo = db_access["update_toldo"]
            update_toldo(
                Toldo_id=Toldo_id,
                modelo=request.form["modelo"],
                tipo=request.form["tipo"],
                dimensiones=request.form["dimensiones"],
            )
            return redirect("/toldo")

    # ------------------VIEW DE Persianas ADMIN-------------------------

    @app.route("/persiana", methods=["GET", "POST"])
    def persiana():

        list_persiana = db_access["list_persianas"]
        persianas = list_persiana()
        usuario = session['usuario']
        usu = usuario
        return render_template("admin/persianas/persianas.html", persianas=persianas, usu=usu)

    @app.route("/create_persiana", methods=["GET", "POST"])
    def create_persiana():
        if request.method == "GET":
            list_persiana = db_access["list_persianas"]
            persianas = list_persiana()
            usuario = session['usuario']
            usu = usuario
            return render_template("admin/persianas/create_persiana.html", persianas=persianas, usu=usu)

        if request.method == "POST":
            create_persiana = db_access["create_persiana"]
            create_persiana(
                modelo=request.form["modelo"],
                tipo=request.form["tipo"],
                dimensiones=request.form["dimensiones"],
                imagen=request.form["imagen"]
            )
            return redirect("/persiana")

    @app.route("/delete_persiana/<int:Persiana_id>", methods=["GET", "POST"])
    def delete_persiana(Persiana_id: int):
        if request.method == "GET":
            read_persiana = db_access["read_persiana"]
            persiana = read_persiana(Persiana_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("admin/persianas/delete_persiana.html", persiana=persiana, usu=usu)

        if request.method == "POST":
            delete_persiana = db_access["delete_persiana"]
            delete_persiana(
                Persiana_id=Persiana_id
            )
            return redirect("/persiana")

    @app.route("/update_persiana/<int:Persiana_id>", methods=["GET", "POST"])
    def updtae_persiana(Persiana_id: int):
        if request.method == "GET":
            read_persiana = db_access["read_persiana"]
            persiana = read_persiana(Persiana_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("admin/persianas/update_persiana.html", persiana=persiana, usu=usu)

        if request.method == "POST":
            update_persiana = db_access["update_persiana"]
            update_persiana(
                Persiana_id=Persiana_id,
                modelo=request.form["modelo"],
                tipo=request.form["tipo"],
                dimensiones=request.form["dimensiones"],
            )
            return redirect("/persiana")

# ------------------VIEW DE Cortinas ADMIN-------------------------

    @app.route("/cortina", methods=["GET", "POST"])
    def cortina():
        list_cortina = db_access["list_cortinas"]
        cortinas = list_cortina()
        usuario = session['usuario']
        usu = usuario
        return render_template("admin/cortinas/cortinas.html", cortinas=cortinas, usu=usu)

    @app.route("/create_cortina", methods=["GET", "POST"])
    def create_cortina():
        if request.method == "GET":
            list_cortina = db_access["list_cortinas"]
            cortinas = list_cortina()
            usuario = session['usuario']
            usu = usuario
            return render_template("admin/cortinas/create_cortina.html", cortinas=cortinas, usu=usu)

        if request.method == "POST":
            create_cortina = db_access["create_cortina"]
            create_cortina(
                tipo=request.form["tipo"],
                tejido=request.form["tejido"],
                estilo=request.form["estilo"],
                imagen=request.form["imagen"]
            )
            return redirect("/cortina")

    @app.route("/update_cortina/<int:Cortina_id>", methods=["GET", "POST"])
    def update_cortina(Cortina_id: int):
        if request.method == "GET":
            read_cortina = db_access["read_cortina"]
            cortina = read_cortina(Cortina_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("admin/cortinas/update_cortina.html", cortina=cortina, usu=usu)

        if request.method == "POST":
            update_cortina = db_access["update_cortina"]
            update_cortina(
                Cortina_id=Cortina_id,
                tipo=request.form["tipo"],
                tejido=request.form["tejido"],
                estilo=request.form["estilo"],
            )
            return redirect("/cortina")

    @app.route("/delete_cortina/<int:Cortina_id>", methods=["GET", "POST"])
    def delete_cortina(Cortina_id: int):
        if request.method == "GET":
            read_cortina = db_access["read_cortina"]
            cortina = read_cortina(Cortina_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("admin/cortinas/delete_cortina.html", cortina=cortina, usu=usu)

        if request.method == "POST":
            delete_cortina = db_access["delete_cortina"]
            delete_cortina(
                Cortina_id=Cortina_id
            )
            return redirect("/cortina")

    # ------------------VIEW DE Toldos USER-------------------------

    @app.route("/toldo_user", methods=["GET", "POST"])
    def toldo_user():
        list_toldo = db_access["list_toldos"]
        toldos = list_toldo()
        usuario = session['usuario']
        usu = usuario

        return render_template("user/toldos_user.html", toldos=toldos, usu=usu)

    # ------------------VIEW DE PERSIANAS USER-------------------------

    @app.route("/persianas_user", methods=["GET", "POST"])
    def persianas_user():
        list_persiana = db_access["list_persianas"]
        persianas = list_persiana()
        usuario = session['usuario']
        usu = usuario

        return render_template("user/persianas/persianas_user.html", persianas=persianas, usu=usu)

    # ------------------VIEW DE CORTINAS USER-------------------------

    @app.route("/cortinas_user", methods=["GET", "POST"])
    def cortinas_user():
        list_cortina = db_access["list_cortinas"]
        cortinas = list_cortina()
        usuario = session['usuario']
        usu = usuario
        return render_template("user/cortinas/cortinas_user.html", cortinas=cortinas, usu=usu)

    @app.route("/details_cortina/<int:Cortina_id>", methods=["GET", "POST"])
    def details_cortina(Cortina_id: int):
        if request.method == "GET":
            read_cortina = db_access["read_cortina"]
            cortina = read_cortina(Cortina_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("user/cortinas/details_cortina.html", cortina=cortina, usu=usu)

        if request.method == "POST":
            usuario = session['usuario']
            usu = usuario
            create_presupuestoC = db_access["create_presupuestoC"]
            create_presupuestoC(
                ancho=request.form["Ancho"],
                alto=request.form["Alto"],
                tejido=request.form["tejido"],
                estilo=request.form["estilo"],
                usuario=usu
            )
            return redirect("/cortinas_user")

    # ------------------VIEW DE DETAILS TOLDO-------------------------

    @app.route("/details_toldo/<int:Toldo_id>", methods=["GET", "POST"])
    def details_toldo(Toldo_id: int):
        if request.method == "GET":
            read_toldo = db_access["read_toldo"]
            toldo = read_toldo(Toldo_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("user/details_toldo.html", toldo=toldo, usu=usu)

        if request.method == "POST":
            usuario = session['usuario']
            usu = usuario
            create_presupuestoT = db_access["create_presupuestoT"]
            create_presupuestoT(
                ancho=request.form["Ancho"],
                salida=request.form["Salida"],
                color=request.form["Color"],
                tipoLona=request.form["Lona"],
                usuario=usu
            )
            return redirect("/toldo_user")
    # ------------------VIEW DE DETAILS persiana-------------------------

    @app.route("/details_persiana/<int:Persiana_id>", methods=["GET", "POST"])
    def details_persiana(Persiana_id: int):
        if request.method == "GET":
            read_persiana = db_access["read_persiana"]
            persiana = read_persiana(Persiana_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("user/persianas/details_persiana.html", persiana=persiana, usu=usu)

        if request.method == "POST":
            usuario = session['usuario']
            usu = usuario
            create_presupuestoP = db_access["create_presupuestoP"]
            create_presupuestoP(
                ancho=request.form["Ancho"],
                alto=request.form["Alto"],
                color=request.form["Color"],
                tipoLama=request.form["Lama"],
                usuario=usu
            )
            return redirect("/persianas_user")

    # ------------------VIEW DE Solicitudes USER-------------------------

    @app.route('/download_pdf_usu/<int:PresupuestoToldo_id>')
    def download_pdf_usu(PresupuestoToldo_id: int):
        read_solicitud = db_access["read_solicitud"]
        factura = read_solicitud(PresupuestoToldo_id)
        # pdf_file_path = os.path.join('\\templates\pdf', str(factura.PresupuestoToldo_id) + str(factura.Usu) + '.pdf')
        # print(pdf_file_path)
        pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf', str(
            factura.PresupuestoToldo_id) + str(factura.Usu) + '.pdf')
        factura_creada = os.path.exists(pdf_file_path)
        if factura_creada:
            return send_file(pdf_file_path, as_attachment=True)
        else:
            # Mostrar mensaje de alerta
            flash('La factura no ha sido creada todavía', 'warning')
            time.sleep(1)  # Esperar 1 segundos antes de redirigir
            return redirect('/solicitudes')

    @app.route("/delete_solicitud_user/<int:PresupuestoToldo_id>", methods=["GET", "POST"])
    def delete_solicitud_user(PresupuestoToldo_id: int):
        if request.method == "POST":
            delete_solicitud = db_access["delete_solicitud"]
            delete_solicitud(
                PresupuestoToldo_id=PresupuestoToldo_id
            )
            return redirect("/solicitudes")

    @app.route("/solicitudes", methods=["GET", "POST"])
    def solicitudes():
        usuario = session['usuario']
        usu = usuario
        list_solicitud = db_access["list_solicitudes_filter"]
        solicitudes = list_solicitud(usu)

        return render_template("user/solicitudes.html", solicitudes=solicitudes, usu=usu)

   # ------------------VIEW DE Solicitudes Persianas USER-------------------------

    @app.route("/solicitudes_p", methods=["GET", "POST"])
    def solicitudes_p():
        usuario = session['usuario']
        usu = usuario
        list_solicitud = db_access["list_solicitudesP_filter"]
        solicitudes = list_solicitud(usu)

        return render_template("user/persianas/solicitudes_p.html", solicitudes=solicitudes, usu=usu)

    @app.route("/delete_p_solicitud_user/<int:PresupuestoPersiana_id>", methods=["GET", "POST"])
    def delete_p_solicitud_user(PresupuestoPersiana_id: int):
        if request.method == "POST":
            delete_solicitud = db_access["delete_solicitud_p"]
            delete_solicitud(
                PresupuestoPersiana_id=PresupuestoPersiana_id
            )
            return redirect("/solicitudes_p")

    @app.route('/download_p_pdf_usu/<int:PresupuestoPersiana_id>')
    def download_p_pdf_usu(PresupuestoPersiana_id: int):
        read_solicitud = db_access["read_solicitud_p"]
        factura = read_solicitud(PresupuestoPersiana_id)
        # pdf_file_path = os.path.join('\\templates\pdf', str(factura.PresupuestoToldo_id) + str(factura.Usu) + '.pdf')
        # print(pdf_file_path)
        pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf\persianas', str(
            factura.PresupuestoPersiana_id) + str(factura.Usu) + '.pdf')
        factura_creada = os.path.exists(pdf_file_path)
        if factura_creada:
            return send_file(pdf_file_path, as_attachment=True)
        else:
            # Mostrar mensaje de alerta
            flash('La factura no ha sido creada todavía', 'warning')
            time.sleep(1)  # Esperar 1 segundos antes de redirigir
            return redirect('/solicitudes_p')

    @app.route("/solicitudes_p_admin", methods=["GET", "POST"])
    def solicitudes_p_admin():
        list_solicitud = db_access["list_solicitudes_p"]
        solicitudes = list_solicitud()
        usuario = session['usuario']
        usu = usuario

        return render_template("admin/persianas/solicitudes_p_admin.html", solicitudes=solicitudes, usu=usu, os=os)

       # ------------------VIEW DE Solicitudes Cortinas -------------------------

    @app.route("/solicitudes_c_admin", methods=["GET", "POST"])
    def solicitudes_c_admin():
        list_solicitud = db_access["list_solicitudes_c"]
        solicitudes = list_solicitud()
        usuario = session['usuario']
        usu = usuario

        return render_template("admin/cortinas/solicitudes_c_admin.html", solicitudes=solicitudes, usu=usu, os=os)

    @app.route("/delete_c_solicitud_user/<int:PresupuestoCortina_id>", methods=["GET", "POST"])
    def delete_c_solicitud_user(PresupuestoCortina_id: int):
        if request.method == "POST":
            delete_solicitud = db_access["delete_solicitud_c"]
            delete_solicitud(
                PresupuestoCortina_id=PresupuestoCortina_id
            )
            return redirect("/solicitudes_c")

    @app.route("/create_factura_c/<int:PresupuestoCortina_id>", methods=["GET", "POST"])
    def create_factura_c(PresupuestoCortina_id: int):
        if request.method == "GET":
            read_solicitud = db_access["read_solicitud_c"]
            factura = read_solicitud(PresupuestoCortina_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("admin/cortinas/create_c_factura.html", factura=factura, usu=usu)
        if request.method == "POST":
            read_solicitud = db_access["read_solicitud_c"]
            factura = read_solicitud(PresupuestoCortina_id)
            my_name = factura.PresupuestoCortina_id
            item1 = factura.Ancho
            item2 = factura.Alto
            item3 = factura.Tejido
            item4 = factura.Estilo
            item5 = factura.Usu
            Pancho = request.form["Pancho"]
            Psalida = request.form["Palto"]
            Pcolor = request.form["Ptejido"]
            Plona = request.form["Pestilo"]
            today_date = datetime.today().strftime("%d/%m/%Y, %H:%M:%S")

            context = {'my_name': my_name, "item1": item1, "item2": item2, "item3": item3, "item4": item4, "item5": item5, "today_date": today_date, "Pancho": Pancho, "Psalida": Psalida,
                       "Pcolor": Pcolor, "Plona": Plona}

            template_loader = jinja2.FileSystemLoader(
                'MolinaWebDesign/myapp/templates/pdf')
            template_env = jinja2.Environment(loader=template_loader)

            html_template = 'plantilla_cortina.html'

            template = template_env.get_template(html_template)

            output_text = template.render(context)

            config = pdfkit.configuration(
                wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

            output_pdf = 'MolinaWebDesign/myapp/templates/pdf/cortinas/' + \
                str(factura.PresupuestoCortina_id) + str(factura.Usu) + '.pdf'

            pdfkit.from_string(output_text, output_pdf, configuration=config)

            print(output_pdf)
            pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf\cortinas', str(
                factura.PresupuestoCortina_id) + str(factura.Usu) + '.pdf')
            return send_file(pdf_file_path, as_attachment=True)

        @app.route('/download_c_pdf_usu/<int:PresupuestoCortina_id>')
        def download_c_pdf_usu(PresupuestoCortina_id: int):
            read_solicitud = db_access["read_solicitud_c"]
            factura = read_solicitud(PresupuestoCortina_id)
            # pdf_file_path = os.path.join('\\templates\pdf', str(factura.PresupuestoToldo_id) + str(factura.Usu) + '.pdf')
            # print(pdf_file_path)
            pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf\cortinas', str(
                factura.PresupuestoCortina_id) + str(factura.Usu) + '.pdf')
            factura_creada = os.path.exists(pdf_file_path)
            if factura_creada:
                return send_file(pdf_file_path, as_attachment=True)
            else:
                # Mostrar mensaje de alerta
                flash('La factura no ha sido creada todavía', 'warning')
                time.sleep(1)  # Esperar 1 segundos antes de redirigir
                return redirect('/solicitudes_c')


# ---------------------------------------------------------------

    @app.route("/create_factura_p/<int:PresupuestoPersiana_id>", methods=["GET", "POST"])
    def create_factura_p(PresupuestoPersiana_id: int):
        if request.method == "GET":
            read_solicitud = db_access["read_solicitud_p"]
            factura = read_solicitud(PresupuestoPersiana_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("admin/persianas/create_p_factura.html", factura=factura, usu=usu)
        if request.method == "POST":
            read_solicitud = db_access["read_solicitud_p"]
            factura = read_solicitud(PresupuestoPersiana_id)
            my_name = factura.PresupuestoPersiana_id
            item1 = factura.Ancho
            item2 = factura.Alto
            item3 = factura.Color
            item4 = factura.TipoLama
            item5 = factura.Usu
            Pancho = request.form["Pancho"]
            Psalida = request.form["Palto"]
            Pcolor = request.form["Pcolor"]
            Plona = request.form["Plama"]
            today_date = datetime.today().strftime("%d/%m/%Y, %H:%M:%S")

            context = {'my_name': my_name, "item1": item1, "item2": item2, "item3": item3, "item4": item4, "item5": item5, "today_date": today_date, "Pancho": Pancho, "Psalida": Psalida,
                       "Pcolor": Pcolor, "Plona": Plona}

            template_loader = jinja2.FileSystemLoader(
                'MolinaWebDesign/myapp/templates/pdf')
            template_env = jinja2.Environment(loader=template_loader)

            html_template = 'plantilla_persiana.html'

            template = template_env.get_template(html_template)

            output_text = template.render(context)

            config = pdfkit.configuration(
                wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

            output_pdf = 'MolinaWebDesign/myapp/templates/pdf/persianas/' + \
                str(factura.PresupuestoPersiana_id) + str(factura.Usu) + '.pdf'

            pdfkit.from_string(output_text, output_pdf, configuration=config)

            print(output_pdf)
            pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf\persianas', str(
                factura.PresupuestoPersiana_id) + str(factura.Usu) + '.pdf')
            return send_file(pdf_file_path, as_attachment=True)

    # ------------------VIEW DE Solicitudes ADMIN-------------------------

    @app.route('/download_pdf/<int:PresupuestoToldo_id>')
    def download_pdf(PresupuestoToldo_id: int):
        read_solicitud = db_access["read_solicitud"]
        factura = read_solicitud(PresupuestoToldo_id)
        pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf', str(
            factura.PresupuestoToldo_id) + str(factura.Usu) + '.pdf')
        # FALTA COMRPOBAR SI EL PDF ESTÁ GENRADO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if os.path.exists(pdf_file_path):
            return send_file(pdf_file_path, as_attachment=True)
        else:
            # Mostrar mensaje de alerta
            flash('La factura no ha sido creada todavía', 'warning')
            time.sleep(5)  # Esperar 5 segundos antes de redirigir
            return redirect('/solicitudes_admin')
        
    @app.route('/download_p_pdf/<int:PresupuestoPersiana_id>')
    def download_p_pdf(PresupuestoPersiana_id: int):
        read_solicitud = db_access["read_solicitud_p"]
        factura = read_solicitud(PresupuestoPersiana_id)
        pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf\persianas', str(
            factura.PresupuestoPersiana_id) + str(factura.Usu) + '.pdf')
        # FALTA COMRPOBAR SI EL PDF ESTÁ GENRADO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if os.path.exists(pdf_file_path):
            return send_file(pdf_file_path, as_attachment=True)
        else:
            # Mostrar mensaje de alerta
            flash('La factura no ha sido creada todavía', 'warning')
            time.sleep(5)  # Esperar 5 segundos antes de redirigir
            return redirect('/solicitudes_p')
        
    @app.route('/download_c_pdf/<int:PresupuestoCortina_id>')
    def download_c_pdf(PresupuestoCortina_id: int):
        read_solicitud = db_access["read_solicitud_c"]
        factura = read_solicitud(PresupuestoCortina_id)
        pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf\cortinas', str(
            factura.PresupuestoCortina_id) + str(factura.Usu) + '.pdf')
        # FALTA COMRPOBAR SI EL PDF ESTÁ GENRADO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if os.path.exists(pdf_file_path):
            return send_file(pdf_file_path, as_attachment=True)
        else:
            # Mostrar mensaje de alerta
            flash('La factura no ha sido creada todavía', 'warning')
            time.sleep(5)  # Esperar 5 segundos antes de redirigir
            return redirect('/solicitudes_c')
    

    @app.route("/delete_solicitud/<int:PresupuestoToldo_id>", methods=["GET", "POST"])
    def delete_solicitud(PresupuestoToldo_id: int):
        if request.method == "POST":
            delete_solicitud = db_access["delete_solicitud"]
            delete_solicitud(
                PresupuestoToldo_id=PresupuestoToldo_id
            )
            return redirect("/solicitudes_admin")

    @app.route("/solicitudes_admin", methods=["GET", "POST"])
    def solicitudes_admin():
        list_solicitud = db_access["list_solicitudes"]
        solicitudes = list_solicitud()
        usuario = session['usuario']
        usu = usuario

        return render_template("solicitudes_admin.html", solicitudes=solicitudes, usu=usu, os=os)

    @app.route("/create_factura/<int:PresupuestoToldo_id>", methods=["GET", "POST"])
    def create_factura(PresupuestoToldo_id: int):
        if request.method == "GET":
            read_solicitud = db_access["read_solicitud"]
            factura = read_solicitud(PresupuestoToldo_id)
            usuario = session['usuario']
            usu = usuario
            return render_template("create_factura.html", factura=factura, usu=usu)
        if request.method == "POST":
            read_solicitud = db_access["read_solicitud"]
            factura = read_solicitud(PresupuestoToldo_id)
            my_name = factura.PresupuestoToldo_id
            item1 = factura.Ancho
            item2 = factura.Salida
            item3 = factura.Color
            item4 = factura.TipoLona
            item5 = factura.Usu
            Pancho = request.form["Pancho"]
            Psalida = request.form["Psalida"]
            Pcolor = request.form["Pcolor"]
            Plona = request.form["Plona"]
            today_date = datetime.today().strftime("%d/%m/%Y, %H:%M:%S")

            context = {'my_name': my_name, "item1": item1, "item2": item2, "item3": item3, "item4": item4, "item5": item5, "today_date": today_date, "Pancho": Pancho, "Psalida": Psalida,
                       "Pcolor": Pcolor, "Plona": Plona}

            template_loader = jinja2.FileSystemLoader(
                'MolinaWebDesign/myapp/templates/pdf')
            template_env = jinja2.Environment(loader=template_loader)

            html_template = 'plantilla.html'

            template = template_env.get_template(html_template)

            output_text = template.render(context)

            config = pdfkit.configuration(
                wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

            output_pdf = 'MolinaWebDesign/myapp/templates/pdf/' + \
                str(factura.PresupuestoToldo_id) + str(factura.Usu) + '.pdf'

            pdfkit.from_string(output_text, output_pdf, configuration=config)
            print(output_pdf)
            pdf_file_path = os.path.join(r'C:\xampp\htdocs\MolinaWebDesign\MolinaWebDesign\myapp\templates\pdf', str(
                factura.PresupuestoToldo_id) + str(factura.Usu) + '.pdf')
            return send_file(pdf_file_path, as_attachment=True)
            # ------------------subir pdf a la bd-------------------------

    # ------------------VIEW DE Solicitudes USER CORTINA-------------------------

    @app.route("/solicitudes_c", methods=["GET", "POST"])
    def solicitudes_c():
        usuario = session['usuario']
        usu = usuario
        list_solicitud = db_access["list_solicitudesC_filter"]
        solicitudes = list_solicitud(usu)

        return render_template("user/cortinas/solicitudes_c.html", solicitudes=solicitudes, usu=usu)

    @app.route("/delete_solicitudC_user/<int:PresupuestoCortina_id>", methods=["GET", "POST"])
    def delete_solicitudC_user(PresupuestoCortina_id: int):
        if request.method == "POST":
            delete_solicitud = db_access["delete_solicitud_c"]
            delete_solicitud(
                PresupuestoCortina_id=PresupuestoCortina_id
            )
            return redirect("/solicitudes_c")
