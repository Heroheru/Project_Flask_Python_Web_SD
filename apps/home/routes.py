# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from jinja2 import TemplateNotFound
import pandas as pd 
import plotly.express as px
from apps.database_coba import Siswa,Kalender_Akademik,Pengumuman, Jadwal_Pelajaran, Guru, Acara_Kegiatan, Mata_Pelajaran, Kelas, Jadwal_Ujian, Profil_Sekolah, Fasilitas_Sekolah, Setting, Foto_Banner, Siswa_Baru, Kelas_Jadwal
from apps import db
from datetime import datetime
import os
from sqlalchemy import func


from werkzeug.utils import secure_filename

# apps\static\tempat_upload_foto
UPLOAD_FOLDER_DB = "../../static/tempat_upload_foto"
UPLOAD_FOLDER = "apps/static/tempat_upload_foto"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#fungsi mendefiniskan hari dalam bahasa indonesia
def get_day_order(day_name):
    hari_indo = {
        "Senin": 0,
        "Selasa": 1,
        "Rabu": 2,
        "Kamis": 3,
        "Jumat": 4,
        "Sabtu": 5,
        "Minggu": 6
    }
    return hari_indo.get(day_name, 7)  # 7 untuk yang tidak dikenal
    
def get_month_name_in_indonesia(month_number):
    bulan_indo = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    return bulan_indo[month_number - 1]  # Menyesuaikan dengan indeks bulan (1-12)

@blueprint.route('/student_page')
def student():
    siswa = Siswa.query.all()  # Query untuk mendapatkan semua pengguna dari database
    kalender_akademik = Kalender_Akademik.query.all()
    pengumuman = Pengumuman.query.all()
    guru = Guru.query.all()
    acara = Acara_Kegiatan.query.all()
    kelas = Kelas.query.all()
    banner = Foto_Banner.query.all()
    setting = Setting.query.first()  # Ambil pengaturan pertama dari tabel Setting
    show_banner = setting.siswa_baru if setting else False  # Tentukan apakah banner ditampilkan

    formatted_kalender = []
    for j in kalender_akademik:
        month_name_in_indonesia_tanggal_mulai = get_month_name_in_indonesia(j.Tanggal_mulai.month)
        month_name_in_indonesia_tanggal_selesai = get_month_name_in_indonesia(j.Tanggal_selesai.month)
        # Format tanggal menjadi format Indonesia
        formatted_tanggal_mulai = j.Tanggal_mulai.strftime(f"%d {month_name_in_indonesia_tanggal_mulai} %Y")  # Menampilkan nama bulan dalam bahasa Indonesia
        formatted_tanggal_selesai = j.Tanggal_selesai.strftime(f"%d {month_name_in_indonesia_tanggal_selesai} %Y")
        formatted_kalender.append({
            'id_kegiatan': j.id_kegiatan,
            'Kegiatan': j.Kegiatan,
            'Tanggal_selesai': j.Tanggal_selesai,
            'Tanggal_mulai': j.Tanggal_mulai,
            'Formatted_tanggal_mulai': formatted_tanggal_mulai,
            'Formatted_tanggal_selesai': formatted_tanggal_selesai})
            
    formatted_kalender.sort(key=lambda j: (
        j['Tanggal_mulai']
            
            
        ))
    return render_template('users_template/home_student.html', segment='student',users=siswa , kegiatan_akademik = formatted_kalender, konten_pengumuman = pengumuman ,data_guru = guru, data_acara= acara, data_kelas = kelas, show_banner = show_banner, gambar_banner = banner, setting = setting)

@blueprint.route('/student_page/kalender_akademik')
def student_kalender_akademik():
   
    kalender_akademik = Kalender_Akademik.query.all()
    setting = Setting.query.first()

    formatted_kalender = []
    for j in kalender_akademik:
        # Ambil nama bulan dari tanggal
        month_name_in_indonesia_tanggal_mulai = get_month_name_in_indonesia(j.Tanggal_mulai.month)
        month_name_in_indonesia_tanggal_selesai = get_month_name_in_indonesia(j.Tanggal_selesai.month)
        # Format tanggal menjadi format Indonesia
        formatted_tanggal_mulai = j.Tanggal_mulai.strftime(f"%d {month_name_in_indonesia_tanggal_mulai} %Y")  # Menampilkan nama bulan dalam bahasa Indonesia
        formatted_tanggal_selesai = j.Tanggal_selesai.strftime(f"%d {month_name_in_indonesia_tanggal_selesai} %Y")
        formatted_kalender.append({
            'id_kegiatan': j.id_kegiatan,
            'Kegiatan': j.Kegiatan,
            'Tanggal_selesai': j.Tanggal_selesai,
            'Tanggal_mulai': j.Tanggal_mulai,
            'Formatted_tanggal_mulai': formatted_tanggal_mulai,
            'Formatted_tanggal_selesai': formatted_tanggal_selesai
        })
            
    formatted_kalender.sort(key=lambda j: (
            j['Tanggal_mulai']
            
            
        ))
    return render_template('users_template/student_kalender_akademik.html', setting = setting,kegiatan_akademik = formatted_kalender)

@blueprint.route('/student_page/find_student_data',methods=['GET', 'POST'])
def find_data_student():
    kelas = Kelas.query.all()
    siswa = []
    setting = Setting.query.first()
    if request.method == 'POST':
        Id_Kelas = request.form['pilih_kelas']
        siswa = Siswa.query.filter_by(kelas=Id_Kelas).order_by(Siswa.nama.asc()).all()  # Ambil data sesuai nama_kelas
        return render_template('users_template/student_tampilkan_siswa_per_kelas.html', setting = setting, segment='student',users=siswa ,data_kelas = kelas)
    return render_template('users_template/find_data_student.html', segment='student',setting = setting, users=siswa ,data_kelas = kelas)


@blueprint.route('/student_page/download_data_siswa_pdf', methods=['POST'])
def download_data_siswa_pdf():
    # Ambil ID kelas yang dipilih dari form
    Id_Kelas = request.form['pilih_kelas']
    # Ambil data jadwal dari database sesuai dengan ID kelas
    siswa = Siswa.query.filter_by(kelas=Id_Kelas).order_by(Siswa.nama.asc()).all()  # Ambil data sesuai nama_kelas
    setting = Setting.query.first()
  

    # Render HTML yang akan dikonversi ke PDF
    rendered_html = render_template('users_template/student_tampilkan_siswa_pdf.html',setting = setting, data_siswa = siswa)

    # Konversi HTML ke PDF
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(rendered_html), dest=pdf)

    # Cek apakah konversi berhasil
    if pisa_status.err:
        return "Gagal membuat PDF", 500

    # Kirim PDF ke pengguna
    pdf.seek(0)
    return make_response(pdf.read(), {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=data_siswa.pdf"
    })
    



@blueprint.route('/student_page/find_jadwal_data', methods=['GET', 'POST'])
def find_data_jadwal_pelajaran():
    kelas = Kelas.query.all()
    setting = Setting.query.first()
    if request.method == 'POST':
        Id_Kelas = request.form['pilih_kelas']
        jadwal = Jadwal_Pelajaran.query.filter_by(id_kelas=Id_Kelas).all()  # Ambil data sesuai nama_kelas
       
        formatted_jadwal = []
        for j in jadwal:
            
            formatted_jadwal.append({
                'id_jadwal': j.id_jadwal,
                'id_kelas': j.id_kelas,
                'hari': j.hari,
                'jam_mulai': j.jam_mulai.strftime('%H:%M'),
                'jam_selesai': j.jam_selesai.strftime('%H:%M'),
                'mata_pelajaran': j.mata_pelajaran,
                'for_kelas' : j.for_kelas,
                'for_matpel' : j.for_matpel
                })
                
        # Urutkan data berdasarkan hari dan jam mulai
        formatted_jadwal.sort(key=lambda j: (
            get_day_order(j['hari']),  # Mengurutkan berdasarkan hari
            datetime.strptime(j['jam_mulai'], "%H:%M")  # Mengurutkan berdasarkan jam mulai
        ))

        return render_template('users_template/student_tampilkan_jadwal_per_kelas.html',setting = setting,data_jadwal=formatted_jadwal, data_kelas = kelas)  # Tampilkan data
    return render_template('users_template/find_data_jadwal.html', segment='student',setting = setting, data_kelas = kelas)

from flask import render_template, request, make_response
from xhtml2pdf import pisa
import io

@blueprint.route('/student_page/download_jadwal_pdf', methods=['POST'])
def download_jadwal_pdf():
    # Ambil ID kelas yang dipilih dari form
    Id_Kelas = request.form['pilih_kelas']
    setting = Setting.query.first()
    # Ambil data jadwal dari database sesuai dengan ID kelas
    jadwal = Jadwal_Pelajaran.query.filter_by(id_kelas=Id_Kelas).all()
    
    # Format data jadwal
    formatted_jadwal = []
    for j in jadwal:
        formatted_jadwal.append({
            'id_jadwal': j.id_jadwal,
            'id_kelas': j.id_kelas,
            'hari': j.hari,
            'jam_mulai': j.jam_mulai.strftime('%H:%M'),
            'jam_selesai': j.jam_selesai.strftime('%H:%M'),
            'mata_pelajaran': j.mata_pelajaran,
            'for_kelas': j.for_kelas,
            'for_matpel': j.for_matpel
        })

    # Render HTML yang akan dikonversi ke PDF
    rendered_html = render_template('users_template/student_tampilkan_jadwal_pdf.html',setting = setting, data_jadwal=formatted_jadwal)

    # Konversi HTML ke PDF
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(rendered_html), dest=pdf)

    # Cek apakah konversi berhasil
    if pisa_status.err:
        return "Gagal membuat PDF", 500

    # Kirim PDF ke pengguna
    pdf.seek(0)
    return make_response(pdf.read(), {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=jadwal_pelajaran.pdf"
    })


#Jadwal Ujian
@blueprint.route('/student_page/cari_jadwal_ujian', methods=['GET', 'POST'])
def find_data_jadwal_ujian():
    kelas = Kelas_Jadwal.query.all()
    setting = Setting.query.first()
    if request.method == 'POST':
        Id_Kelas = request.form['pilih_kelas']
        jadwal_ujian = Jadwal_Ujian.query.filter_by(kelas=Id_Kelas).all()  # Ambil data sesuai nama_kelas
        formatted_jadwal = []
        for j in jadwal_ujian:
            # Ambil nama bulan dari tanggal
            month_name_in_indonesia = get_month_name_in_indonesia(j.tanggal.month)

            # Format tanggal menjadi format Indonesia
            formatted_tanggal = j.tanggal.strftime(f"%d {month_name_in_indonesia} %Y")  # Menampilkan nama bulan dalam bahasa Indonesia
            
            formatted_jadwal.append({
                
                'id_jadwal_ujian': j.id_jadwal_ujian,
                'kelas': j.kelas,
                'hari': j.hari,
                'tanggal': j.tanggal,  # Tanggal asli
                'formatted_tanggal': formatted_tanggal,
                'mata_pelajaran': j.mata_pelajaran,
                'pengawas':j.pengawas,
                'keterangan': j.keterangan,
                'foreign_kelas' : j.foreign_kelas,
                'for_matpel' : j.for_matpel,
                'for_guru' : j.for_guru 
                
                })
        
        formatted_jadwal.sort(key=lambda j: (
            j['tanggal'],
            get_day_order(j['hari'])  # Mengurutkan berdasarkan hari
            
        ))

        return render_template('users_template/student_tampilkan_jadwal_ujian_per_kelas.html',setting = setting,data_jadwal=formatted_jadwal, data_kelas = kelas)  # Tampilkan data
    return render_template('users_template/find_data_jadwal_ujian.html', segment='student', setting = setting,data_kelas = kelas)

from flask import render_template, request, make_response
from xhtml2pdf import pisa
import io

@blueprint.route('/student_page/download_jadwal_ujian_pdf', methods=['POST'])
def download_jadwal_ujian_pdf():
    # Ambil ID kelas yang dipilih dari form
    Id_Kelas = request.form['pilih_kelas']
    setting = Setting.query.first()
    # Ambil data jadwal dari database sesuai dengan ID kelas
    jadwal = Jadwal_Ujian.query.filter_by(kelas=Id_Kelas).all()
    
    # Format data jadwal
    formatted_jadwal_ujian = []
    for j in jadwal:
        
        # Ambil nama bulan dari tanggal
        month_name_in_indonesia = get_month_name_in_indonesia(j.tanggal.month)

        # Format tanggal menjadi format Indonesia
        formatted_tanggal = j.tanggal.strftime(f"%d {month_name_in_indonesia} %Y")  # Menampilkan nama bulan dalam bahasa Indonesia
        
        formatted_jadwal_ujian.append({
                'id_jadwal_ujian': j.id_jadwal_ujian,
                'kelas': j.kelas,
                'hari': j.hari,
                'tanggal': j.tanggal,
                'formatted_tanggal': formatted_tanggal,
                'mata_pelajaran': j.mata_pelajaran,
                'pengawas':j.pengawas,
                'keterangan': j.keterangan,
                'foreign_kelas' : j.foreign_kelas,
                'for_matpel' : j.for_matpel,
                'for_guru' : j.for_guru 
        })
        
    formatted_jadwal_ujian.sort(key=lambda j: (
        j['tanggal'],
        get_day_order(j['hari'])  # Mengurutkan berdasarkan hari
            
         # Mengurutkan berdasarkan hari
            
    ))

    # print(formatted_jadwal_ujian)
    # Render HTML yang akan dikonversi ke PDF
    rendered_html = render_template('users_template/student_tampilkan_jadwal_ujian_pdf.html',setting = setting, data_jadwal=formatted_jadwal_ujian)

    # Konversi HTML ke PDF
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(rendered_html), dest=pdf)

    # Cek apakah konversi berhasil
    if pisa_status.err:
        return "Gagal membuat PDF", 500

    # Kirim PDF ke pengguna
    pdf.seek(0)
    return make_response(pdf.read(), {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=jadwal_ujian.pdf"
    })

@blueprint.route('/student_page/pengumuman<int:id_pengumuman>')
def show_pengumuman(id_pengumuman):
    pengumuman = Pengumuman.query.get_or_404(id_pengumuman)  # Query untuk mendapatkan semua pengguna dari database
    return render_template('users_template/student_pengumuman.html', segment='student',konten_pengumuman = pengumuman)

@blueprint.route('/student_page/data_kelas')
def show_kelas():
    kelas = Kelas.query.all()  # Query untuk mendapatkan semua pengguna dari database   
    setting = Setting.query.first() 
    return render_template('users_template/student_tampilkan_data_kelas.html', segment='student',setting = setting,data_kelas = kelas)

@blueprint.route('/student_page/data_guru')
def show_guru():
    guru = Guru.query.all()  # Query untuk mendapatkan semua pengguna dari database    
    return render_template('users_template/student_tampilkan_data_guru.html', segment='student',data_guru = guru)

@blueprint.route('/student_page/kegiatan')
def show_kegiatan():
    acara = Acara_Kegiatan.query.all()  # Query untuk mendapatkan semua pengguna dari database    
    return render_template('users_template/student_tampilkan_kegiatan.html', segment='student',data_acara = acara)
    
@blueprint.route('/student_page/profil_sekolah')
def show_profil_sekolah():
    profsekolah = Profil_Sekolah.query.all()  # Query untuk mendapatkan semua pengguna dari database    
    return render_template('users_template/student_tampilkan_profil_sekolah.html', segment='student',data_profil = profsekolah)

@blueprint.route('/student_page/fasilitas_sekolah')
def show_fasilitas_sekolah():
    fasilsekolah = Fasilitas_Sekolah.query.all()  # Query untuk mendapatkan semua pengguna dari database    
    return render_template('users_template/student_tampilkan_fasilitas_sekolah.html', segment='student',data_fasilitas = fasilsekolah)

@blueprint.route('/student_page/siswa_baru')
def student_siswa_baru():
    setting = Setting.query.first()  # Ambil pengaturan pertama dari tabel Setting
    siswa_baru = Siswa_Baru.query.all()  # Query untuk mendapatkan semua pengguna dari database    
    return render_template('users_template/student_siswa_baru.html', segment='student',setting=setting,data_siswa = siswa_baru)










# @blueprint.route('/Admin')
# @login_required
# def index():
#     # Data untuk plot
#     df = pd.DataFrame({
#         "X": [1, 2, 3, 4, 5],
#         "Y": [10, 11, 12, 13, 14],
#         "Label": ["A", "B", "C", "D", "E"]
#     })

#     # Membuat plot interaktif
#     fig = px.bar(df, x="X", y="Y", text="Label", title="Grafik Interaktif dengan Plotly")
    
#     # Menyimpan grafik dalam format HTML
#     graph_html = fig.to_html(full_html=False)
#     return render_template('home/index.html', segment='index',graph_html=graph_html)


#SISWA_BARU
@blueprint.route('/Admin/Admin_Data_siswa_baru')
@login_required
def admin_edit_data_siswa_baru():
    siswa_baru = Siswa_Baru.query.order_by(Siswa_Baru.nama_siswa_baru.desc()).all()  # Query untuk mendapatkan semua pengguna dari database
    return render_template('users_template/admin_data_siswa_baru.html', segment='admin',users=siswa_baru)

@blueprint.route('/Admin/tambah_siswa_baru', methods=['GET', 'POST'])
@login_required
def tambah_siswa_baru():
    if request.method == 'POST':
        try:
            siswa_baru = Siswa_Baru(
                nama_siswa_baru = request.form['nama_siswa_baru'],
                nomor_identitas = request.form['nomor_identitas']
                
            )


            db.session.add(siswa_baru)
            db.session.commit()
      
            return redirect(url_for('home_blueprint.admin_edit_data_siswa_baru'))
        
        except Exception as e:
            db.session.rollback()
            print('GAGAL', {str(e)})
            flash(f'Gagal menambahkan siswa: {str(e)}', 'danger')
   
    return render_template('users_template/admin_tambah_siswa_baru.html')  # Tampilkan form tambah siswa

@blueprint.route('/Admin/update_siswa_baru/<int:siswa_id>', methods=['GET', 'POST'])
@login_required
def update_siswa_baru(siswa_id):
    siswa_baru = Siswa_Baru.query.get_or_404(siswa_id)  # Ambil data siswa berdasarkan ID
    if request.method == 'POST':
        try:
            siswa_baru.nama_siswa_baru = request.form['nama_siswa_baru']
            siswa_baru.nomor_identitas = request.form['nomor_identitas']
            
            # Update data lain sesuai kebutuhan

            db.session.commit()
     
            return redirect(url_for('home_blueprint.admin_edit_data_siswa_baru'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupdate data siswa: {str(e)}', 'danger')
    
    return render_template('users_template/admin_update_siswa_baru.html', data_siswa=siswa_baru)


@blueprint.route('/delete_siswa_baru/<int:siswa_id>', methods=['GET', 'POST'])
@login_required
def delete_siswa_baru(siswa_id):
    siswa_baru= Siswa_Baru.query.get_or_404(siswa_id)  # Mengambil siswa berdasarkan ID
    db.session.delete(siswa_baru)  # Menghapus siswa dari session
    db.session.commit()  # Menyimpan perubahan ke database
    return redirect(url_for('home_blueprint.admin_edit_data_siswa_baru'))  # Kembali ke daftar siswa




#SISWA
@blueprint.route('/Admin/Admin_Data_siswa')
@login_required
def admin_edit_data_student():
    siswa = Siswa.query.order_by(Siswa.nipd.desc()).all()  # Query untuk mendapatkan semua pengguna dari database
    return render_template('users_template/admin_data_student.html', segment='admin',users=siswa)

@blueprint.route('/Admin/tambah_siswa', methods=['GET', 'POST'])
@login_required
def tambah_siswa():
    print(request.form)
    kelas = Kelas.query.all()
    if request.method == 'POST':
        try:
            siswa_baru = Siswa(
                nama = request.form['nama_siswa'],
                nisn = request.form['nis'],
                nipd = request.form['nipd'],
                nik = request.form['nik'],
                tempat_lahir = request.form['tempat_lahir'],
                tanggal_lahir = request.form['tanggal_lahir'],
                jk = request.form['jenis_kelamin'],
                kelas = request.form['id_kelas'],
                agama = request.form['agama'],
                alamat = request.form['alamat'],
                rt = request.form['rt'],
                rw = request.form['rw'],
                dusun = request.form['dusun'],
                kelurahan = request.form['kelurahan'],
                kecamatan = request.form['kecamatan'],
                kode_pos = request.form['kode_pos'],
                jenis_tinggal = request.form['jenis_tinggal'],
                alat_transportasi = request.form['alat_transportasi'],
                no_hp = request.form['no_hp'],
                email = request.form['email'],
                skhun = request.form['skhun'],
                penerima_kps = request.form['penerima_kps'],
                no_kps = request.form['no_kps'],
                nama_ayah=request.form['nama_ayah'],
                tahun_lahir_ayah = request.form['tahun_lahir_ayah'],
                pekerjaan_ayah = request.form['pekerjaan_ayah'],
                penghasilan_ayah = request.form.get('penghasilan_ayah', ''),
                jenjang_pendidikan_ayah = request.form.get('jenjang_pendidikan_ayah', ''),
                nik_ayah = request.form['nik_ayah'],
                nama_ibu=request.form['nama_ibu'],
                tahun_lahir_ibu = request.form['tahun_lahir_ibu'],
                pekerjaan_ibu = request.form['pekerjaan_ibu'],
                penghasilan_ibu = request.form.get('penghasilan_ibu', ''),
                jenjang_pendidikan_ibu = request.form.get('jenjang_pendidikan_ibu', ''),
                nik_ibu = request.form['nik_ibu'],
                nama_wali=request.form['nama_wali'],
                tahun_lahir_wali = request.form['tahun_lahir_wali'],
                pekerjaan_wali = request.form['pekerjaan_wali'],
                penghasilan_wali = request.form.get('penghasilan_wali', ''),
                jenjang_pendidikan_wali = request.form.get('jenjang_pendidikan_wali', ''),
                nik_wali = request.form['nik_wali'],
                no_peserta_ujian_nasional = request.form['no_peserta_ujian_nasional'],
                no_seri_ijazah = request.form['no_seri_ijazah'],
                penerima_kip = request.form['penerima_kip'],
                nomor_kip = request.form['nomor_kip'],
                nama_kip = request.form['nama_kip'],
                nomor_kks = request.form['nomor_kks'],
                noreg_akta_lahir = request.form['noreg_akta_lahir'],
                bank = request.form['bank'],
                no_rek_bank = request.form['no_rek_bank'],
                nama_rek_bank = request.form['nama_rek_bank'],
                layak_pip = request.form['layak_pip'],
                alasan_layak_pip = request.form['alasan_layak_pip'],
                kebutuhan_khusus = request.form['kebutuhan_khusus'],
                sekolah_asal = request.form['sekolah_asal'],
                anak_ke = request.form['anak_ke'],
                lintang = request.form['lintang'],
                bujur = request.form['bujur'],
                no_kk = request.form['no_kk'],
                berat_badan = request.form['berat_badan'],
                tinggi_badan =request.form['tinggi_badan'],
                lingkar_kepala = request.form['lingkar_kepala'],
                jml_saudara = request.form['jml_saudara'],
                jarak_rumah_sekolah = request.form['jarak_rumah_sekolah']
                # Tambahkan data lain sesuai kebutuhan
            )

            print(siswa_baru)

            db.session.add(siswa_baru)
            db.session.commit()
      
            return redirect(url_for('home_blueprint.admin_edit_data_student'))
        
        except Exception as e:
            db.session.rollback()
            import traceback
            print('GAGAL:', traceback.format_exc())
           
   
    return render_template('users_template/admin_tambah_siswa.html', data_kelas = kelas)  # Tampilkan form tambah siswa

@blueprint.route('/Admin/update_siswa/<int:siswa_id>', methods=['GET', 'POST'])
@login_required
def update_siswa(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)  # Ambil data siswa berdasarkan ID
    kelas = Kelas.query.all()
    if request.method == 'POST':
        try:
            siswa.nama = request.form['nama_siswa']
            siswa.nisn = request.form['nis']
            siswa.nipd = request.form['nipd']
            siswa.nik = request.form['nik']
            siswa.tempat_lahir = request.form['tempat_lahir']
            siswa.tanggal_lahir = request.form['tanggal_lahir']
            siswa.jk = request.form['jenis_kelamin']
            siswa.kelas = request.form['id_kelas']
            siswa.agama = request.form['agama']
            siswa.alamat = request.form['alamat']
            siswa.rt = request.form['rt']
            siswa.rw = request.form['rw']
            siswa.dusun = request.form['dusun']
            siswa.kelurahan = request.form['kelurahan']
            siswa.kecamatan = request.form['kecamatan']
            siswa.kode_pos = request.form['kode_pos']
            siswa.jenis_tinggal = request.form['jenis_tinggal']
            siswa.alat_transportasi = request.form['alat_transportasi']
            siswa.no_hp = request.form['no_hp']
            siswa.email = request.form['email']
            siswa.skhun = request.form['skhun']
            siswa.penerima_kps = request.form['penerima_kps']
            siswa.no_kps = request.form['no_kps']
            siswa.nama_ayah=request.form['nama_ayah']
            siswa.tahun_lahir_ayah = request.form['tahun_lahir_ayah']
            siswa.pekerjaan_ayah = request.form['pekerjaan_ayah']
            siswa.penghasilan_ayah = request.form['penghasilan_ayah']
            siswa.jenjang_pendidikan_ayah = request.form['jenjang_pendidikan_ayah']
            siswa.nik_ayah = request.form['nik_ayah']
            siswa.nama_ibu=request.form['nama_ibu']
            siswa.tahun_lahir_ibu = request.form['tahun_lahir_ibu']
            siswa.pekerjaan_ibu = request.form['pekerjaan_ibu']
            siswa.penghasilan_ibu = request.form['penghasilan_ibu']
            siswa.jenjang_pendidikan_ibu = request.form['jenjang_pendidikan_ibu']
            siswa.nik_ibu = request.form['nik_ibu']
            siswa.nama_wali=request.form['nama_wali']
            siswa.tahun_lahir_wali = request.form['tahun_lahir_wali']
            siswa.pekerjaan_wali = request.form['pekerjaan_wali']
            siswa.penghasilan_wali = request.form['penghasilan_wali']
            siswa.jenjang_pendidikan_wali = request.form['jenjang_pendidikan_wali']
            siswa.nik_wali = request.form['nik_wali']
            siswa.no_peserta_ujian_nasional = request.form['no_peserta_ujian_nasional']
            siswa.no_seri_ijazah = request.form['no_seri_ijazah']
            siswa.penerima_kip = request.form['penerima_kip']
            siswa.nomor_kip = request.form['nomor_kip']
            siswa.nama_kip = request.form['nama_kip']
            siswa.nomor_kks = request.form['nomor_kks']
            siswa.noreg_akta_lahir = request.form['noreg_akta_lahir']
            siswa.bank = request.form['bank']
            siswa.no_rek_bank = request.form['no_rek_bank']
            siswa.nama_rek_bank = request.form['nama_rek_bank']
            siswa.layak_pip = request.form['layak_pip']
            siswa.alasan_layak_pip = request.form['alasan_layak_pip']
            siswa.kebutuhan_khusus = request.form['kebutuhan_khusus']
            siswa.sekolah_asal = request.form['sekolah_asal']
            siswa.anak_ke = request.form.get('anak_ke', type=int)
            siswa.lintang = request.form.get('lintang', type=float)
            siswa.bujur = request.form.get('bujur', type=float)
            siswa.no_kk = request.form['no_kk']
            siswa.berat_badan = request.form.get('berat_badan', type=float)
            siswa.tinggi_badan = request.form.get('tinggi_badan', type=float)
            siswa.lingkar_kepala = request.form.get('lingkar_kepala', type=float)
            siswa.jml_saudara = request.form.get('jml_saudara', type=int)
            siswa.jarak_rumah_sekolah = request.form.get('jarak_rumah_sekolah', type=float)
            # Update data lain sesuai kebutuhan

            db.session.commit()
            flash('Data siswa berhasil diupdate!', 'success')
            return redirect(url_for('home_blueprint.admin_edit_data_student'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupdate data siswa: {str(e)}', 'danger')
    
    return render_template('users_template/admin_update_siswa.html', data_siswa=siswa, data_kelas = kelas)


@blueprint.route('/delete/<int:siswa_id>', methods=['GET', 'POST'])
@login_required
def delete_siswa_page(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)  # Mengambil siswa berdasarkan ID
    db.session.delete(siswa)  # Menghapus siswa dari session
    db.session.commit()  # Menyimpan perubahan ke database
    return redirect(url_for('home_blueprint.admin_edit_data_student'))  # Kembali ke daftar siswa


@blueprint.route('/Admin/show_siswa/<int:siswa_id>', methods=['GET', 'POST'])
@login_required
def admin_show_detail_data_siswa(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)  # Ambil data siswa berdasarkan ID 
    return render_template('users_template/admin_show_detail_siswa.html', data_siswa=siswa)

@blueprint.route('/Admin/download_datasiswa_pdf', methods=['POST'])
@login_required
def admin_download_biodata_siswa():
    # Ambil ID kelas yang dipilih dari form
    siswa_id = request.form['nisn']
    # Ambil data jadwal dari database sesuai dengan ID kelas
    data_siswa = Siswa.query.filter_by(nisn = siswa_id).one_or_none()  # Ambil data sesuai nama_kelas
    
    
    if data_siswa is None:
        return "Guru tidak ditemukan", 404  # Kembali dengan pesan error jika tidak ada

    # Render HTML yang akan dikonversi ke PDF
    rendered_html = render_template('users_template/admin_show_detail_siswa_pdf.html', siswa = data_siswa)

    # Konversi HTML ke PDF
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(rendered_html, dest=pdf)

    # Cek apakah konversi berhasil
    if pisa_status.err:
        return "Gagal membuat PDF", 500

    # Kirim PDF ke pengguna
    pdf.seek(0)
    return make_response(pdf.read(), {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=data_siswa.pdf"
    })

from flask import  send_file
import pandas as pd
from io import BytesIO
from sqlalchemy.orm import joinedload
import tempfile


@blueprint.route('Admin/bcjwqhbcjwbcjqwbcjhwvjvchjwevucywe/bevh/fff/fjwejhcjhwevchewvhcbewbcwbechbew/echwhcqwh',methods=['GET', 'POST'])
@login_required
def admin_download_excel_siswa():
    # Query all data from the Siswa model
    siswa_data = Siswa.query.options(joinedload(Siswa.for_kelas)).order_by(Siswa.kelas.asc()).all()

    # Convert the data into a list of dictionaries
    data_list = []
    for siswa in siswa_data:
        siswa_dict = {
            'Nama': siswa.nama,
            'NIPD': siswa.nipd,
            'JK': siswa.jk,
            'NISN': siswa.nisn,
            'Tempat Lahir': siswa.tempat_lahir,
            'Tanggal Lahir': siswa.tanggal_lahir,
            'Agama': siswa.agama,
            'Alamat': siswa.alamat,
            'RT': siswa.rt,
            'RW': siswa.rw,
            'Dusun': siswa.dusun,
            'Kelurahan': siswa.kelurahan,
            'Kecamatan': siswa.kecamatan,
            'Kode Pos': siswa.kode_pos,
            'Jenis Tinggal': siswa.jenis_tinggal,
            'Alat Transportasi': siswa.alat_transportasi,
            'No HP': siswa.no_hp,
            'Email': siswa.email,
            'SKHUN' : siswa.skhun,
            'Penerima KPS': siswa.penerima_kps,
            'No KPS': siswa.no_kps,
            'Nama Ayah': siswa.nama_ayah,
            'Tahun Lahir Ayah': siswa.tahun_lahir_ayah,
            'Jenjang Pendidikan Ayah': siswa.jenjang_pendidikan_ayah,
            'Pekerjaan Ayah': siswa.pekerjaan_ayah,
            'Penghasilan Ayah': siswa.penghasilan_ayah,
            'NIK Ayah': siswa.nik_ayah,
            'Nama Ibu': siswa.nama_ibu,
            'Tahun Lahir Ibu': siswa.tahun_lahir_ibu,
            'Jenjang Pendidikan Ibu': siswa.jenjang_pendidikan_ibu,
            'Pekerjaan Ibu': siswa.pekerjaan_ibu,
            'Penghasilan Ibu': siswa.penghasilan_ibu,
            'NIK Ibu': siswa.nik_ibu,
            'Nama Wali': siswa.nama_wali,
            'Tahun Lahir Wali': siswa.tahun_lahir_wali,
            'Jenjang Pendidikan Wali': siswa.jenjang_pendidikan_wali,
            'Pekerjaan Wali': siswa.pekerjaan_wali,
            'Penghasilan Wali': siswa.penghasilan_wali,
            'NIK Wali': siswa.nik_wali,
            'Kelas': siswa.for_kelas.nama_kelas if siswa.for_kelas else None,
            'No Peserta Ujian Nasional': siswa.no_peserta_ujian_nasional,
            'No Seri Ijazah': siswa.no_seri_ijazah,
            'Penerima KIP': siswa.penerima_kip,
            'Nomor KIP': siswa.nomor_kip,
            'Nama KIP': siswa.nama_kip,
            'Nomor KKS': siswa.nomor_kks,
            'No Reg Akta Lahir': siswa.noreg_akta_lahir,
            'Bank': siswa.bank,
            'No Rek Bank': siswa.no_rek_bank,
            'Nama Rek Bank': siswa.nama_rek_bank,
            'Layak PIP': siswa.layak_pip,
            'Alasan Layak PIP': siswa.alasan_layak_pip,
            'Kebutuhan Khusus': siswa.kebutuhan_khusus,
            'Sekolah Asal': siswa.sekolah_asal,
            'Anak Ke': siswa.anak_ke,
            'Lintang': siswa.lintang,
            'Bujur': siswa.bujur,
            'No KK': siswa.no_kk,
            'Berat Badan': siswa.berat_badan,
            'Tinggi Badan': siswa.tinggi_badan,
            'Lingkar Kepala': siswa.lingkar_kepala,
            'Jumlah Saudara': siswa.jml_saudara,
            'Jarak Rumah Sekolah': siswa.jarak_rumah_sekolah

            # Add all other columns as needed
        }
        data_list.append(siswa_dict)

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(data_list)

    # # Create a BytesIO buffer to store the Excel file in memory
    # output = BytesIO()

    # # Write the DataFrame to the Excel buffer
    # with pd.ExcelWriter(output, engine='openpyxl') as writer:
    #     df.to_excel(writer, index=False, sheet_name='Siswa Data')

    # # Seek to the beginning of the buffer
    # output.seek(0)

    # # Send the Excel file as a response
    # return send_file(output, as_attachment=True, download_name='siswa_data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
        print("File sementara disimpan di:", temp.name)

        # Tulis DataFrame ke file Excel
        with pd.ExcelWriter(temp.name, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Siswa Data')

        # Simpan path file untuk digunakan nanti
        temp_path = temp.name

    # Kirim file sebagai respons Flask
    response = send_file(
        temp_path,
        as_attachment=True,
        download_name='siswa_data.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Hapus file sementara setelah respons selesai
    @response.call_on_close
    def cleanup():
        try:
            os.remove(temp_path)
            print(f"File sementara dihapus: {temp_path}")
        except Exception as e:
            print(f"Error saat menghapus file sementara: {e}")

    return response
        
       



#GURU


@blueprint.route('/Admin/Admin_data_guru')
@login_required
def admin_edit_data_guru():
    guru = Guru.query.order_by(Guru.nip.desc()).all()  # Query untuk mendapatkan semua pengguna dari database
    return render_template('users_template/admin_data_guru.html', segment='admin',data_guru=guru)

from flask import request, jsonify

import tinify
# Set your TinyJPG API key
tinify.key = 'XGTZJ9ZnqrP02wtzPv6nHGYsQ3WJKw7Y'

def optimize_image_tinyjpg(image_path):
    try:
        # Kompresi gambar menggunakan TinyJPG
        source = tinify.from_file(image_path)
        source.to_file(image_path)  # Simpan gambar yang sudah dikompresi kembali ke path yang sama
    except tinify.errors.AccountError:
        flash("API key TinyJPG tidak valid.")
    except tinify.errors.ClientError:
        flash("Gagal mengoptimalkan gambar.")
    except tinify.errors.ServerError:
        flash("Terjadi kesalahan pada server TinyJPG.")
    except tinify.errors.ConnectionError:
        flash("Gagal terhubung dengan server TinyJPG.")
    except Exception as e:
        flash(f"Terjadi kesalahan: {str(e)}")
        
        

@blueprint.route('/Admin/Admin_data_guru/tambah_guru', methods=['GET', 'POST'])
@login_required
def admin_tambah_data_guru():
    UPLOAD_FOLDER_GURU = "apps/static/tempat_upload_foto/Foto_Guru"
    UPLOAD_FOLDER_DB = "../../static/tempat_upload_foto/Foto_Guru"
    if request.method == 'POST':
        try:
            image_guru = request.files['image_path_guru']


        # Jika file valid dan diizinkan
            if image_guru and allowed_file(image_guru.filename):
                filename = secure_filename(image_guru.filename)
                filepath = os.path.join(UPLOAD_FOLDER_GURU, filename)
                filepath_for_db = os.path.join(UPLOAD_FOLDER_DB, filename).replace("\\", "/")
                image_guru.save(filepath)
                
                # Optimasi dengan TinyJPG
                optimize_image_tinyjpg(filepath)
                
                flash('File berhasil diunggah')
            else:
                # Tidak ada file yang diunggah, gunakan path gambar lama dari database
                filepath_for_db = "../../static/assets/img/Logo_Orang.png"

            guru_baru = Guru(
                nama = request.form['nama'],
                nip = request.form['nip'],
                jk = request.form['jk'],
                tempat_lahir = request.form['tempat_lahir'],
                tanggal_lahir = request.form['tanggal_lahir'],
                agama = request.form['agama'],
                status = request.form['status'],
                golongan = request.form['golongan'],
                status_perkawinan = request.form['status_perkawinan'],
                jml_anak = request.form['jml_anak'],
                masa_kerja_thn = request.form['masa_kerja_thn'],
                masa_kerja_bln = request.form['masa_kerja_bln'],
                tmt_sd = request.form['tmt_sd'],
                pendidikan = request.form['pendidikan'],
                jurusan = request.form['jurusan'],
                lulus = request.form['lulus'],
                kelas_ajar = request.form['kelas_ajar'],
                jam_week = request.form['jam_week'],
                image_path_guru = filepath_for_db
        )
            
       
            db.session.add(guru_baru)
            db.session.commit()
            
            return redirect(url_for('home_blueprint.admin_edit_data_guru'))
          
        except KeyError as e:
            # Menangani error jika ada field yang tidak ditemukan
            return jsonify({"error": f"Field '{e.args[0]}' tidak ditemukan dalam form"}), 400
        except Exception as e:
            # Tangani error lainnya
            db.session.rollback()
            return jsonify({"error": "Terjadi kesalahan saat menambahkan data"}), 500
        # except Exception as e:
        #     db.session.rollback()
        #     flash(f'Gagal menambahkan siswa: {str(e)}', 'danger')
    return render_template('users_template/admin_tambah_guru.html', segment='admin')

def get_existing_image_path_from_db(guru_id):
    guru = Guru.query.get_or_404(guru_id)  # Cari guru berdasarkan ID
    return guru.image_path_guru if guru else None  # Kembalikan path gambar jika ada

@blueprint.route('/Admin/update_guru/<int:guru_id>', methods=['GET', 'POST'])
@login_required
def admin_update_data_guru(guru_id):
    guru = Guru.query.get_or_404(guru_id)  # Ambil data siswa berdasarkan ID
    UPLOAD_FOLDER_GURU = "apps/static/tempat_upload_foto/Foto_Guru"
    UPLOAD_FOLDER_DB = "../../static/tempat_upload_foto/Foto_Guru"
    if request.method == 'POST':
        try:
            image_guru = request.files.get('image_path_guru')

        # Jika file valid dan diizinkan
            if image_guru and image_guru.filename != '' and allowed_file(image_guru.filename):
                filename = secure_filename(image_guru.filename)
                filepath = os.path.join(UPLOAD_FOLDER_GURU, filename)
                filepath_for_db = os.path.join(UPLOAD_FOLDER_DB, filename).replace("\\", "/")
                image_guru.save(filepath)
                optimize_image_tinyjpg(filepath)
                flash('File berhasil diunggah')
            else:
                # Tidak ada file yang diunggah, gunakan path gambar lama dari database
                filepath_for_db = get_existing_image_path_from_db(guru_id)

            guru.nama = request.form['nama']
            guru.nip = request.form['nip']
            guru.jk = request.form['jk']
            guru.tempat_lahir = request.form['tempat_lahir']
            guru.tanggal_lahir = request.form['tanggal_lahir']
            guru.agama = request.form['agama']
            guru.status = request.form['status']
            guru.golongan = request.form['golongan']
            guru.status_perkawinan = request.form['status_perkawinan']
            guru.jml_anak = request.form['jml_anak']
            guru.masa_kerja_thn = request.form['masa_kerja_thn']
            guru.masa_kerja_bln = request.form['masa_kerja_bln']
            guru.tmt_sd = request.form['tmt_sd']
            guru.pendidikan = request.form['pendidikan']
            guru.jurusan = request.form['jurusan']
            guru.lulus = request.form['lulus']
            guru.kelas_ajar = request.form['kelas_ajar']
            guru.jam_week = request.form['jam_week']
            guru.image_path_guru = filepath_for_db
           
            db.session.commit()
            flash('Data siswa berhasil diupdate!', 'success')
            return redirect(url_for('home_blueprint.admin_edit_data_guru'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupdate data siswa: {str(e)}', 'danger')
    
    return render_template('users_template/admin_update_guru.html', data_guru=guru)

@blueprint.route('/Admin/show_guru/<int:guru_id>', methods=['GET', 'POST'])
@login_required
def admin_show_detail_data_guru(guru_id):
    guru = Guru.query.get_or_404(guru_id)  # Ambil data siswa berdasarkan ID 
    return render_template('users_template/admin_show_detail_guru.html', data_guru=guru)


@blueprint.route('/Admin/download_data_guru_pdf', methods=['POST'])
@login_required
def admin_download_biodata_guru():
    # Ambil ID kelas yang dipilih dari form
    guru_id = request.form['id_guru']
    # Ambil data jadwal dari database sesuai dengan ID kelas
    guru = Guru.query.filter_by(id_guru = guru_id).one_or_none()  # Ambil data sesuai nama_kelas
    print(guru.image_path_guru)
    
    if guru is None:
        return "Guru tidak ditemukan", 404  # Kembali dengan pesan error jika tidak ada

    # Render HTML yang akan dikonversi ke PDF
    rendered_html = render_template('users_template/admin_show_detail_guru_pdf.html', data_guru =guru)

    # Konversi HTML ke PDF
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(rendered_html, dest=pdf)

    # Cek apakah konversi berhasil
    if pisa_status.err:
        return "Gagal membuat PDF", 500

    # Kirim PDF ke pengguna
    pdf.seek(0)
    return make_response(pdf.read(), {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=data_siswa.pdf"
    })



@blueprint.route('Admin/delete_guru/<int:guru_id>', methods=['GET', 'POST'])
@login_required
def admin_delete_data_guru(guru_id):
    guru = Guru.query.get_or_404(guru_id)  # Mengambil siswa berdasarkan ID
    db.session.delete(guru)  # Menghapus siswa dari session
    db.session.commit()  # Menyimpan perubahan ke database
    return redirect(url_for('home_blueprint.admin_edit_data_guru'))  # Kembali ke daftar siswa

@blueprint.route('Admin/bhebdjjewbfjhwjhb33rg3we3bfewgfejhbfjewgbejwbfebgfye/bfjwbfhwfhebjhfbejfbjebw',methods=['GET', 'POST'])
@login_required
def admin_download_excel_guru():
    # Query all data from the Siswa model
    guru_data = Guru.query.options().order_by(Guru.nama.asc()).all()

    # Convert the data into a list of dictionaries
    data_list = []
    for guru in guru_data:
        guru_dict = {
            'Nama': guru.nama,
            'NIP': guru.nip,
            'JK': guru.jk,
            'Tempat Lahir': guru.tempat_lahir,
            'Tanggal Lahir': guru.tanggal_lahir,
            'Agama': guru.agama,
            'Status': guru.status,
            'Golongan': guru.golongan,
            'Status Perkawinan': guru.status_perkawinan,
            'Jumlah Anak': guru.jml_anak,
            'Masa Kerja Tahun': guru.masa_kerja_thn,
            'Masa Kerja Bulan': guru.masa_kerja_bln,
            'TMT SD': guru.tmt_sd,
            'Pendidikan': guru.pendidikan,
            'Jurusan': guru.jurusan,
            'Lulus': guru.lulus,
            'Kelas Ajar': guru.kelas_ajar,
            'Jam per Minggu': guru.jam_week
        }

            
        data_list.append(guru_dict)

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(data_list)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
        print("File sementara disimpan di:", temp.name)

        # Tulis DataFrame ke file Excel
        with pd.ExcelWriter(temp.name, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Guru Data')

        # Simpan path file untuk digunakan nanti
        temp_path = temp.name

    # Kirim file sebagai respons Flask
    response = send_file(
        temp_path,
        as_attachment=True,
        download_name='guru_data.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Hapus file sementara setelah respons selesai
    @response.call_on_close
    def cleanup():
        try:
            os.remove(temp_path)
            print(f"File sementara dihapus: {temp_path}")
        except Exception as e:
            print(f"Error saat menghapus file sementara: {e}")

    return response


@blueprint.route('/Admin/Admin_Data_Kalender_Akademik')
@login_required
def admin_edit_data_kalender():
    kalender_akademik = Kalender_Akademik.query.all()  # Query untuk mendapatkan semua pengguna dari database
    formatted_kalender = []
    for j in kalender_akademik:
        month_name_in_indonesia_tanggal_mulai = get_month_name_in_indonesia(j.Tanggal_mulai.month)
        month_name_in_indonesia_tanggal_selesai = get_month_name_in_indonesia(j.Tanggal_selesai.month)
        # Format tanggal menjadi format Indonesia
        formatted_tanggal_mulai = j.Tanggal_mulai.strftime(f"%d {month_name_in_indonesia_tanggal_mulai} %Y")  # Menampilkan nama bulan dalam bahasa Indonesia
        formatted_tanggal_selesai = j.Tanggal_selesai.strftime(f"%d {month_name_in_indonesia_tanggal_selesai} %Y")
        formatted_kalender.append({
            'id_kegiatan': j.id_kegiatan,
            'Kegiatan': j.Kegiatan,
            'Tanggal_selesai': j.Tanggal_selesai,
            'Tanggal_mulai': j.Tanggal_mulai,
            'Formatted_tanggal_mulai': formatted_tanggal_mulai,
            'Formatted_tanggal_selesai': formatted_tanggal_selesai})
            
    formatted_kalender.sort(key=lambda j: (
        j['Tanggal_mulai']
            
            
        ))
    return render_template('users_template/admin_edit_data_kalender.html', segment='admin',kegiatan_akademik = formatted_kalender)


@blueprint.route('/Admin/Admin_Data_Kalender_Akademik/tambah_kalender_akademik', methods=['GET', 'POST'])
def tambah_kalender():
    if request.method == 'POST':
        nama_kegiatan = request.form['nama_kegiatan']
        tanggal_mulai = request.form['tanggal_mulai']
        tanggal_selesai = request.form['tanggal_selesai']
        
        
        # Membuat objek siswa baru
        kegiatan_baru = Kalender_Akademik(Kegiatan=nama_kegiatan, Tanggal_mulai = tanggal_mulai, Tanggal_selesai =  tanggal_selesai)
        
        # Menyimpan ke database
        db.session.add(kegiatan_baru)
        db.session.commit()
        
        return redirect(url_for('home_blueprint.admin_edit_data_kalender'))  # Kembali ke daftar siswa setelah menambah data
    # return render_template('student/add_siswa.html')  # Tampilkan form tambah siswa

@blueprint.route('/Admin/Admin_Data_Kalender_Akademik/delete/<int:kegiatan_id>', methods=['GET', 'POST'])
@login_required
def delete_kalender(kegiatan_id):
    kalender = Kalender_Akademik.query.get_or_404(kegiatan_id)  # Mengambil siswa berdasarkan ID
    db.session.delete(kalender)  # Menghapus siswa dari session
    db.session.commit()  # Menyimpan perubahan ke database
    return redirect(url_for('home_blueprint.admin_edit_data_kalender'))  # Kembali ke daftar siswa


@blueprint.route('/Admin/Admin_Data_Kalender_Akademik/update/<int:kegiatan_id>', methods=['GET', 'POST'])
@login_required
def update_kalender(kegiatan_id):
    kegiatan = Kalender_Akademik.query.get_or_404(kegiatan_id)  # Mengambil siswa berdasarkan ID
    if request.method == 'POST':
        # Mengupdate data siswa dengan data dari form
        kegiatan.Kegiatan = request.form['nama_kegiatan']
        kegiatan.Tanggal_mulai = request.form['tanggal_mulai']
        kegiatan.Tanggal_selesai = request.form['tanggal_selesai']
        db.session.commit()  # Menyimpan perubahan ke database
        return redirect(url_for('home_blueprint.admin_edit_data_kalender'))  # Kembali ke daftar siswa
    # return render_template('student/home_student.html')  # Tampilkan form untuk update


#KELAS WALIKELAS
@blueprint.route('/Admin/Admin_Data_Kelas_Walas')
@login_required
def admin_edit_data_kelas_walas():
    kelas_walas = Kelas.query.all()  # Query untuk mendapatkan semua pengguna dari database
    guru = Guru.query.all()
    return render_template('users_template/admin_edit_data_kelas_walas.html', segment='admin',kelas = kelas_walas, data_guru = guru)

@blueprint.route('/Admin/Admin_Data_Kelas_Walas/tambah_kelas_walas', methods=['GET', 'POST'])
@login_required
def tambah_kelas():
    if request.method == 'POST':
        nama_kelas = request.form['nama_kelas']
        id_wali_kelas = request.form['id_wali_kelas']
    
    
        # Membuat objek siswa baru
        kelas_baru = Kelas(nama_kelas = nama_kelas,id_wali_kelas = id_wali_kelas)
        
        # Menyimpan ke database
        db.session.add(kelas_baru)
        db.session.commit()
        
        return redirect(url_for('home_blueprint.admin_edit_data_kelas_walas'))  # Kembali ke daftar siswa setelah menambah data
  

@blueprint.route('/Admin/Admin_Data_Kelas_walas/update/<int:kelas_id>', methods=['GET', 'POST'])
@login_required
def update_kelas(kelas_id):
    kelas = Kelas.query.get_or_404(kelas_id)  # Mengambil siswa berdasarkan ID
    if request.method == 'POST':
        # Mengupdate data siswa dengan data dari form
        kelas.nama_kelas = request.form['nama_kelas']
        kelas.id_wali_kelas = request.form['id_wali_kelas']
        
        db.session.commit()  # Menyimpan perubahan ke database
        return redirect(url_for('home_blueprint.admin_edit_data_kelas_walas'))  # Kembali ke daftar siswa
    # return render_template('student/home_student.html')  # Tampilkan form untuk update

@blueprint.route('/Admin/Admin_Data_Kelas_walas/delete/<int:kelas_id>', methods=['GET', 'POST'])
@login_required
def delete_kelas(kelas_id):
    kelas = Kelas.query.get_or_404(kelas_id)  # Mengambil siswa berdasarkan ID
    db.session.delete(kelas)  # Menghapus siswa dari session
    db.session.commit()  # Menyimpan perubahan ke database
    return redirect(url_for('home_blueprint.admin_edit_data_kelas_walas'))  # Kembali ke daftar siswa



#Mata Pelajaran
@blueprint.route('/Admin/Admin_Data_Matpel')
@login_required
def admin_edit_data_matpel():
    matpel = Mata_Pelajaran.query.all()  # Query untuk mendapatkan semua pengguna dari database
    return render_template('users_template/admin_edit_data_matpel.html', segment='admin',data_matpel = matpel)

@blueprint.route('/Admin/Admin_Data_Matpel/tambah_mata_pelajaran', methods=['GET', 'POST'])
@login_required
def tambah_matpel():
    if request.method == 'POST':
        nama_matpel = request.form['nama_matpel']
        
        # Membuat objek siswa baru
        matpel_baru = Mata_Pelajaran(nama_mata_pelajaran  = nama_matpel)
        
        # Menyimpan ke database
        db.session.add(matpel_baru)
        db.session.commit()
        
        return redirect(url_for('home_blueprint.admin_edit_data_matpel'))  # Kembali ke daftar siswa setelah menambah data
  

@blueprint.route('/Admin/Admin_Data_Matpel/update/<int:matpel_id>', methods=['GET', 'POST'])
@login_required
def update_matpel(matpel_id):
    matpel = Mata_Pelajaran.query.get_or_404(matpel_id)  # Mengambil siswa berdasarkan ID
    if request.method == 'POST':
        # Mengupdate data siswa dengan data dari form
        matpel.nama_mata_pelajaran = request.form['nama_matpel']
    
        
        db.session.commit()  # Menyimpan perubahan ke database
        return redirect(url_for('home_blueprint.admin_edit_data_matpel'))  # Kembali ke daftar siswa


@blueprint.route('/Admin/Admin_Data_Matpel/delete/<int:matpel_id>', methods=['GET', 'POST'])
@login_required
def delete_matpel(matpel_id):
    matpel = Mata_Pelajaran.query.get_or_404(matpel_id)  # Mengambil siswa berdasarkan ID
    db.session.delete(matpel)  # Menghapus siswa dari session
    db.session.commit()  # Menyimpan perubahan ke database
    return redirect(url_for('home_blueprint.admin_edit_data_matpel'))  # Kembali ke daftar siswa

#PENGUMUMAN


@blueprint.route('/Admin/Admin_Pengumuman')
@login_required
def admin_pengumuman():
    pengumuman = Pengumuman.query.all()
    return render_template('users_template/admin_pengumuman.html', segment='admin', konten_pengumuman = pengumuman)


@blueprint.route('/Admin/Admin_Pengumuman/tambah_pengumuman' , methods=['GET', 'POST'])
@login_required
def admin_tambah_pengumuman():
    if request.method == 'POST':
        # Memeriksa apakah ada file dalam request
        judul_pengumuman = request.form['judul_pengumuman']
        konten_pengumuman = request.form['content_pengumuman']
        gambar_pengumuman = request.files['gambar']
        current_time = datetime.now()

        if 'gambar' not in request.files:
            return redirect(request.url)

        # Jika file valid dan diizinkan
        if gambar_pengumuman and allowed_file(gambar_pengumuman.filename):
            filename = secure_filename(gambar_pengumuman.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            filepath_for_db = os.path.join(UPLOAD_FOLDER_DB, filename).replace("\\", "/")
            gambar_pengumuman.save(filepath)
            optimize_image_tinyjpg(filepath)
            # gambar_pengumuman.save(UPLOAD_FOLDER, filename)
            flash('File berhasil diunggah')
        else:
            filepath_for_db = None  # Jika tidak ada gambar, set path ke None
            #  Membuat objek siswa baru
        pengumuman_baru = Pengumuman(judul_pengumuman=judul_pengumuman, isi = konten_pengumuman,image_path=filepath_for_db, tanggal = current_time )
        
            # Menyimpan ke database
        db.session.add(pengumuman_baru)
        db.session.commit()
        return redirect(url_for('home_blueprint.admin_pengumuman'))
          
    return render_template('users_template/admin_tambah_pengumuman.html', segment='admin')


def get_existing_image_path_pengumuman_from_db(id_pengumuman):
    pengumuman = Pengumuman.query.get_or_404(id_pengumuman)  # Cari guru berdasarkan ID
    return pengumuman.image_path if pengumuman else None  # Kembalikan path gambar jika ada

@blueprint.route('/Admin/Admin_Pengumuman/edit_pengumuman<int:id_pengumuman>' , methods=['GET', 'POST'])
@login_required
def admin_edit_pengumuman(id_pengumuman):
    pengumuman = Pengumuman.query.get_or_404(id_pengumuman)
    if request.method == 'POST':
        try:
            image_pengumuman = request.files.get('gambar')

        # Jika file valid dan diizinkan
            if image_pengumuman and image_pengumuman.filename != '' and allowed_file(image_pengumuman.filename):
                filename = secure_filename(image_pengumuman.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                filepath_for_db = os.path.join(UPLOAD_FOLDER_DB, filename).replace("\\", "/")
                image_pengumuman.save(filepath)
                optimize_image_tinyjpg(filepath)
                
            else:
                # Tidak ada file yang diunggah, gunakan path gambar lama dari database
                filepath_for_db = get_existing_image_path_pengumuman_from_db(id_pengumuman)
                      
            pengumuman.judul_pengumuman = request.form['judul_pengumuman']
            pengumuman.isi = request.form['content_pengumuman']
            pengumuman.image_path = filepath_for_db
            pengumuman.tanggal =         current_time = datetime.now()
            db.session.commit()
            return redirect(url_for('home_blueprint.admin_pengumuman'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupdate data siswa: {str(e)}', 'danger')
     
    # if request.method == 'POST':
    #     pengumuman.judul_pengumuman = request.form['judul_pengumuman']
    #     pengumuman.isi = request.form['content_pengumuman']
    #     pengumuman.tanggal =         current_time = datetime.now()
    #     db.session.commit()
    #     return redirect(url_for('home_blueprint.admin_pengumuman'))
    return render_template('users_template/admin_edit_pengumuman.html', segment='admin', konten_pengumuman = pengumuman)


@blueprint.route('/Admin/Admin_Pengumuman/delete_pengumuman<int:id_pengumuman>' , methods=['GET', 'POST'])
@login_required
def admin_delete_pengumuman(id_pengumuman):
    
    pengumuman = Pengumuman.query.get_or_404(id_pengumuman) 
    db.session.delete(pengumuman)
    db.session.commit()
    return redirect(url_for('home_blueprint.admin_pengumuman'))



#KEGIATAN


@blueprint.route('/Admin/Admin_Kegiatan')
@login_required
def admin_kegiatan():
    acara = Acara_Kegiatan.query.all()
    return render_template('users_template/admin_kegiatan.html', segment='admin', data_kegiatan = acara)


@blueprint.route('/Admin/Admin_Kegiatan/tambah_kegiatan' , methods=['GET', 'POST'])
@login_required
def admin_tambah_kegiatan():
    if request.method == 'POST':
 
        UPLOAD_FOLDER_DB_KEGIATAN = "../../static/tempat_upload_foto/Foto_Kegiatan"
        UPLOAD_FOLDER_KEGIATAN = "apps/static/tempat_upload_foto/Foto_Kegiatan"    
        # Memeriksa apakah ada file dalam request
        judul_kegiatan= request.form['judul_kegiatan']
        konten_kegiatan = request.form['konten_kegiatan']
        gambar_kegiatan = request.files['gambar_kegiatan']
        tanggal_kegiatan = request.form['tanggal_kegiatan']
        filepath_for_db = None 
        if 'gambar_kegiatan' not in request.files:
            flash('Tidak ada gambar yang diunggah')
            return redirect(request.url)

        # Jika file valid dan diizinkan
        if gambar_kegiatan and allowed_file(gambar_kegiatan.filename):
            filename = secure_filename(gambar_kegiatan.filename)
            filepath = os.path.join(UPLOAD_FOLDER_KEGIATAN, filename)
            filepath_for_db = os.path.join(UPLOAD_FOLDER_DB_KEGIATAN, filename).replace("\\", "/")
            gambar_kegiatan.save(filepath)
            optimize_image_tinyjpg(filepath)
            # gambar_pengumuman.save(UPLOAD_FOLDER, filename)
            flash('File berhasil diunggah')
            #  Membuat objek siswa baru
        kegiatan_baru = Acara_Kegiatan(nama_kegiatan= judul_kegiatan, konten_kegiatan= konten_kegiatan,img_path_kegiatan=filepath_for_db, tanggal_kegiatan= tanggal_kegiatan )
  
        
            # Menyimpan ke database
        db.session.add(kegiatan_baru)
        db.session.commit()
        return redirect(url_for('home_blueprint.admin_kegiatan'))
          
    return render_template('users_template/admin_tambah_kegiatan.html', segment='admin')


def get_existing_image_path_kegiatan_from_db(id_kegiatan):
    kegiatan = Acara_Kegiatan.query.get_or_404(id_kegiatan)  # Cari guru berdasarkan ID
    return kegiatan.img_path_kegiatan if kegiatan else None  # Kembalikan path gambar jika ada

@blueprint.route('/Admin/Admin_Kegiatan/edit_kegiatan<int:id_kegiatan>' , methods=['GET', 'POST'])
@login_required
def admin_edit_kegiatan(id_kegiatan):
    kegiatan = Acara_Kegiatan.query.get_or_404(id_kegiatan) 
    UPLOAD_FOLDER_DB_KEGIATAN = "../../static/tempat_upload_foto/Foto_Kegiatan"
    UPLOAD_FOLDER_KEGIATAN = "apps/static/tempat_upload_foto/Foto_Kegiatan"    
    if request.method == 'POST':
        try:
            image_kegiatan = request.files.get('gambar_kegiatan')

        # Jika file valid dan diizinkan
            if image_kegiatan and image_kegiatan.filename != '' and allowed_file(image_kegiatan.filename):
                filename = secure_filename(image_kegiatan.filename)
                filepath = os.path.join(UPLOAD_FOLDER_KEGIATAN, filename)
                filepath_for_db = os.path.join(UPLOAD_FOLDER_DB_KEGIATAN, filename).replace("\\", "/")
                image_kegiatan.save(filepath)
                optimize_image_tinyjpg(filepath)
                flash('File berhasil diunggah')
            else:
                # Tidak ada file yang diunggah, gunakan path gambar lama dari database
                filepath_for_db = get_existing_image_path_kegiatan_from_db(id_kegiatan)

            kegiatan.nama_kegiatan= request.form['judul_kegiatan']
            kegiatan.konten_kegiatan = request.form['konten_kegiatan']
            kegiatan.img_path_kegiatan = filepath_for_db
            kegiatan.tanggal_kegiatan = request.form['tanggal_kegiatan']
            
            db.session.commit()
            flash('Data kegiatan siswa berhasil diupdate!', 'success')
            return redirect(url_for('home_blueprint.admin_kegiatan'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupdate data siswa: {str(e)}', 'danger')
    
    return render_template('users_template/admin_update_kegiatan.html', segment='admin', data_kegiatan=kegiatan)






@blueprint.route('/Admin/Admin_Kegiatan/delete_kegiatan<int:id_kegiatan>' , methods=['GET', 'POST'])
@login_required
def admin_delete_kegiatan(id_kegiatan):
    kegiatan = Acara_Kegiatan.query.get_or_404(id_kegiatan) 
    db.session.delete(kegiatan)
    db.session.commit()
    return redirect(url_for('home_blueprint.admin_kegiatan'))

    

#JADWAL PELAJARAN
@blueprint.route('/Admin/Admin_Data_Jadwal')
@login_required
def admin_edit_data_jadwal():
    jadwal = Jadwal_Pelajaran.query.all()  # Ambil data sesuai nama_kelas
    matpel = Mata_Pelajaran.query.all()
    kelas = Kelas.query.all()
    formatted_jadwal = []
    for j in jadwal:
        formatted_jadwal.append({
            'id_jadwal': j.id_jadwal,
            'id_kelas': j.id_kelas,
            'hari': j.hari,
            'jam_mulai': j.jam_mulai.strftime('%H:%M'),
            'jam_selesai': j.jam_selesai.strftime('%H:%M'),
            'mata_pelajaran': j.mata_pelajaran,
            'for_kelas' : j.for_kelas,
            'for_matpel' : j.for_matpel })
    return render_template('users_template/admin_edit_jadwal_per_kelas.html',data_jadwal=formatted_jadwal, data_matpel = matpel, data_kelas = kelas)  # Tampilkan data

@blueprint.route('/Admin/Admin_Data_Jadwal/tambah_data_jadwal', methods=['GET', 'POST'])
@login_required
def admin_add_data_jadwal():
    if request.method == 'POST':
        id_kelas = request.form['id_kelas']
        hari = request.form['hari']
        jam_mulai = request.form['jam_mulai']
        jam_selesai = request.form['jam_selesai']
        mata_pelajaran = request.form['mata_pelajaran']
     
        
        
        # Membuat objek siswa baru
        jadwal_baru = Jadwal_Pelajaran(id_kelas = id_kelas, hari = hari, jam_mulai = jam_mulai, jam_selesai = jam_selesai, mata_pelajaran = mata_pelajaran)
        
        # Menyimpan ke database
        db.session.add(jadwal_baru)
        db.session.commit()
        
        return redirect(url_for('home_blueprint.admin_edit_data_jadwal'))  # Kembali ke daftar siswa setelah menambah data
    # return render_template('student/add_siswa.html')  # Tampilkan form tambah siswa


@blueprint.route('/Admin/Admin_Data_Jadwal/edit_data_jadwal<int:jadwal_id>' , methods=['GET', 'POST'])
@login_required
def update_jadwal_siswa(jadwal_id):
    jadwal_pelajaran = Jadwal_Pelajaran.query.get_or_404(jadwal_id) 
    if request.method == 'POST':
        jadwal_pelajaran.id_kelas = request.form['id_kelas']
        jadwal_pelajaran.hari = request.form['hari']
        jadwal_pelajaran.jam_mulai = request.form['jam_mulai']
        jadwal_pelajaran.jam_selesai = request.form['jam_selesai']
        jadwal_pelajaran.mata_pelajaran = request.form['mata_pelajaran']
        db.session.commit()
        return redirect(url_for('home_blueprint.admin_edit_data_jadwal'))
    

@blueprint.route('/Admin/Admin_Data_Jadwal/delete_data_jadwal<int:jadwal_id>' , methods=['GET', 'POST'])
@login_required
def admin_delete_jadwal_siswa(jadwal_id):
    jadwal_pelajaran = Jadwal_Pelajaran.query.get_or_404(jadwal_id) 
    db.session.delete(jadwal_pelajaran)
    db.session.commit()
    return redirect(url_for('home_blueprint.admin_edit_data_jadwal'))



#JADWAL Ujian
@blueprint.route('/Admin/Admin_Data_Jadwal_Ujian')
@login_required
def admin_edit_data_jadwal_ujian():
    jadwal_ujian = Jadwal_Ujian.query.all()  # Ambil data sesuai nama_kelas
    matpel = Mata_Pelajaran.query.all()
    kelas = Kelas_Jadwal.query.all()
    guru = Guru.query.all()
    formatted_jadwal = []
    for j in jadwal_ujian:
        formatted_jadwal.append({
            'id_jadwal_ujian': j.id_jadwal_ujian,
            'kelas': j.kelas,
            'hari': j.hari,
            'tanggal': j.tanggal,
            'mata_pelajaran': j.mata_pelajaran,
            'pengawas':j.pengawas,
            'keterangan': j.keterangan,
            'foreign_kelas' : j.foreign_kelas,
            'for_matpel' : j.for_matpel,
            'for_guru' : j.for_guru })
        
    return render_template('users_template/admin_edit_jadwal_ujian.html',jadwal_ujian=formatted_jadwal, data_kelas = kelas, data_matpel = matpel, data_guru=guru)  # Tampilkan data

@blueprint.route('/Admin/Admin_Data_Jadwal_Ujian/tambah_data_jadwa_ujianl', methods=['GET', 'POST'])
@login_required
def admin_add_data_jadwal_ujian():
    if request.method == 'POST':
        kelas = request.form['kelas']
        hari = request.form['hari']
        tanggal = request.form['tanggal']
        mata_pelajaran = request.form['mata_pelajaran']
        pengawas = request.form['pengawas']
        keterangan = request.form['keterangan']
        
        
        # Membuat objek siswa baru
        jadwal_ujian_baru = Jadwal_Ujian(kelas = kelas, hari = hari, tanggal = tanggal, mata_pelajaran = mata_pelajaran, pengawas= pengawas, keterangan=keterangan)
        
        # Menyimpan ke database
        db.session.add(jadwal_ujian_baru)
        db.session.commit()
        
        return redirect(url_for('home_blueprint.admin_edit_data_jadwal_ujian'))  # Kembali ke daftar siswa setelah menambah data
    # return render_template('student/add_siswa.html')  # Tampilkan form tambah siswa


@blueprint.route('/Admin/Admin_Data_Jadwal_Ujian/edit_data_jadwal_ujian<int:jadwal_ujian_id>' , methods=['GET', 'POST'])
@login_required
def update_jadwal_ujian(jadwal_ujian_id):
    jadwal_ujian = Jadwal_Ujian.query.get_or_404(jadwal_ujian_id) 
    if request.method == 'POST':
        jadwal_ujian.kelas = request.form['kelas']
        jadwal_ujian.hari = request.form['hari']
        jadwal_ujian.tanggal = request.form['tanggal']
        jadwal_ujian.mata_pelajaran = request.form['mata_pelajaran']
        jadwal_ujian.pengawas = request.form['pengawas']
        jadwal_ujian.keterangan = request.form['keterangan']
        db.session.commit()
        return redirect(url_for('home_blueprint.admin_edit_data_jadwal_ujian'))
    

@blueprint.route('/Admin/Admin_Data_Jadwal_Ujian/delete_data_jadwal_ujian<int:jadwal_ujian_id>' , methods=['GET', 'POST'])
@login_required
def admin_delete_jadwal_ujian(jadwal_ujian_id):
    jadwal_ujian = Jadwal_Ujian.query.get_or_404(jadwal_ujian_id) 
    db.session.delete(jadwal_ujian)
    db.session.commit()
    return redirect(url_for('home_blueprint.admin_edit_data_jadwal_ujian'))

#PROFILE SEKOLAH

@blueprint.route('/Admin/Admin_Profile_sekolah_sekolah/edit_profile<int:id_profile_sekolah>' , methods=['GET', 'POST'])
@login_required
def admin_edit_profile_sekolah(id_profile_sekolah):
    profil = Profil_Sekolah.query.get_or_404(id_profile_sekolah) 
  
    if request.method == 'POST':
       
        profil.nama_sklh = request.form['nama_sklh']
        profil.nis = request.form['nis']
        profil.nss = request.form['nss']
        profil.provinsi = request.form['provinsi']
        profil.otonomi = request.form['otonomi']
        profil.kecamatan = request.form['kecamatan']
        profil.desa_kelurahan = request.form['desa_kelurahan']
        profil.jln_no = request.form['jln_no']
        profil.kode_pos = request.form['kode_pos']
        profil.telepon = request.form['telepon']
        profil.faximile = request.form['faximile']
        profil.daerah = request.form['daerah']
        profil.status_sklh = request.form['status_sklh']
        profil.kelompok_sklh = request.form['kelompok_sklh']
        profil.akreditasi = request.form['akreditasi']
        profil.surat_keputusan_sk = request.form['surat_keputusan_sk']
        profil.tanggal_sk = request.form['tanggal_sk']
        profil.penerbit_sk = request.form['penerbit_sk']
        profil.thn_berdiri = request.form['thn_berdiri']
        profil.thn_perubahan = request.form['thn_perubahan']
        profil.kegiatan_bljr_mengajar = request.form['kegiatan_bljr_mengajar']
        profil.bangunan_sklh = request.form['bangunan_sklh']
        profil.luas_bangunan = request.form['luas_bangunan']
        profil.lokasi_sklh = request.form['lokasi_sklh']
        profil.jarak_kecamatan = request.form['jarak_kecamatan']
        profil.jarak_otoda = request.form['jarak_otoda']
        profil.terletak_pd_lintasan = request.form['terletak_pd_lintasan']
        profil.jmlh_keanggotaan_gugus = request.form['jmlh_keanggotaan_gugus']
        profil.organisasi_penyelenggara = request.form['organisasi_penyelenggara']
        profil.perjalanan_perubahan_sklh = request.form['perjalanan_perubahan_sklh']
            
        db.session.commit()
        return redirect(url_for('home_blueprint.admin_edit_profile_sekolah', id_profile_sekolah=1))
    
    return render_template('users_template/admin_edit_profil_sekolah.html', segment='admin', profil=profil)

   
#FASILITAS


@blueprint.route('/Admin/Admin_Fasilitas')
@login_required
def admin_fasilitas():
    fasilitas = Fasilitas_Sekolah.query.all()
    return render_template('users_template/admin_fasilitas.html', segment='admin', data_fasilitas = fasilitas)


@blueprint.route('/Admin/Admin_Fasilitas/tambah_fasilitas' , methods=['GET', 'POST'])
@login_required
def admin_tambah_fasilitas():
    if request.method == 'POST':
        UPLOAD_FOLDER_DB_FASILITAS = "../../static/tempat_upload_foto/Foto_Fasilitas"
        UPLOAD_FOLDER_FASILITAS = "apps/static/tempat_upload_foto/Foto_Fasilitas"    
        # Memeriksa apakah ada file dalam request
        nama_fasilitas= request.form['nama_fasilitas']
        gambar_fasilitas = request.files['gambar_fasilitas']
        filepath_for_db = None 
        if 'gambar_fasilitas' not in request.files:
            flash('Tidak ada gambar yang diunggah')
            return redirect(request.url)

        # Jika file valid dan diizinkan
        if gambar_fasilitas and allowed_file(gambar_fasilitas.filename):
            filename = secure_filename(gambar_fasilitas.filename)
            filepath = os.path.join(UPLOAD_FOLDER_FASILITAS, filename)
            filepath_for_db = os.path.join(UPLOAD_FOLDER_DB_FASILITAS, filename).replace("\\", "/")
            print(filepath_for_db)
            gambar_fasilitas.save(filepath)
            optimize_image_tinyjpg(filepath)
            # gambar_pengumuman.save(UPLOAD_FOLDER, filename)
            flash('File berhasil diunggah')
            #  Membuat objek siswa baru
        fasilitas_baru = Fasilitas_Sekolah(nama_fasilitas= nama_fasilitas, gambar_fasilitas=filepath_for_db )
  
        
            # Menyimpan ke database
        db.session.add(fasilitas_baru)
        db.session.commit()
        return redirect(url_for('home_blueprint.admin_fasilitas'))
          
    return render_template('users_template/admin_tambah_fasilitas.html', segment='admin')


def get_existing_image_path_fasilitas_from_db(id_fasilitas):
    fasilitas = Fasilitas_Sekolah.query.get_or_404(id_fasilitas)  # Cari guru berdasarkan ID
    return fasilitas.gambar_fasilitas if fasilitas else None  # Kembalikan path gambar jika ada

@blueprint.route('/Admin/Admin_Fasilitas/edit_fasilitas<int:id_fasilitas>' , methods=['GET', 'POST'])
@login_required
def admin_edit_fasilitas(id_fasilitas):
    fasilitas = Fasilitas_Sekolah.query.get_or_404(id_fasilitas) 
    UPLOAD_FOLDER_DB_FASILITAS = "../../static/tempat_upload_foto/Foto_Fasilitas"
    UPLOAD_FOLDER_FASILITAS = "apps/static/tempat_upload_foto/Foto_Fasilitas"    
      
    if request.method == 'POST':
        try:
            gambar_fasilitas = request.files.get('gambar_fasilitas')

        # Jika file valid dan diizinkan
            if gambar_fasilitas and gambar_fasilitas.filename != '' and allowed_file(gambar_fasilitas.filename):
                filename = secure_filename(gambar_fasilitas.filename)
                filepath = os.path.join(UPLOAD_FOLDER_FASILITAS, filename)
                filepath_for_db = os.path.join(UPLOAD_FOLDER_DB_FASILITAS, filename).replace("\\", "/")
                gambar_fasilitas.save(filepath)
                optimize_image_tinyjpg(filepath)
                flash('File berhasil diunggah')
            else:
                # Tidak ada file yang diunggah, gunakan path gambar lama dari database
                filepath_for_db = get_existing_image_path_fasilitas_from_db(id_fasilitas)

            fasilitas.nama_fasilitas= request.form['nama_fasilitas']
            fasilitas.gambar_fasilitas = filepath_for_db

            
            db.session.commit()

            return redirect(url_for('home_blueprint.admin_fasilitas'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupdate data fasilitas: {str(e)}', 'danger')
    
    return render_template('users_template/admin_update_fasilitas.html', segment='admin', data_fasilitas=fasilitas)






@blueprint.route('/Admin/Admin_Fasilitas/delete_fasilitas<int:id_fasilitas>' , methods=['GET', 'POST'])
@login_required
def admin_delete_fasilitas(id_fasilitas):
    fasilitas = Fasilitas_Sekolah.query.get_or_404(id_fasilitas) 
    db.session.delete(fasilitas)
    db.session.commit()
    return redirect(url_for('home_blueprint.admin_fasilitas'))

@blueprint.route('/Admin/Admin_Setting' , methods=['GET', 'POST'])
@login_required
def admin_settings():
    setting = Setting.query.first()
    if request.method == 'POST':
        # Cek apakah checkbox 'siswa_baru' dicentang
        siswa_baru = 'siswa_baru' in request.form
        semester = request.form['semester']
        tahun_ajaran = request.form['tahun_ajaran']
        assesment_sumatif = request.form['ASM']
        # Update status siswa_baru
        setting.siswa_baru = siswa_baru
        setting.semester = semester
        setting.tahun_ajaran = tahun_ajaran
        setting.assesment_sumatif = assesment_sumatif
        db.session.commit()  # Simpan perubahan ke database
        return redirect(url_for('home_blueprint.admin_settings'))
    
    # Kirim setting ke template
    return render_template('users_template/admin_setting.html', setting=setting)  



#banner_photo
@blueprint.route('/Admin/Admin_Banner_Photo')
@login_required
def admin_banner_photo():
    banner = Foto_Banner.query.all()
    return render_template('users_template/admin_banner_photo.html', segment='admin', data_banner = banner)


@blueprint.route('/Admin/Admin_Banner_Photo/tambah_banner' , methods=['GET', 'POST'])
@login_required
def admin_tambah_banner():
    if request.method == 'POST':
        UPLOAD_FOLDER_DB_BANNER = "../../static/tempat_upload_foto/Foto_Banner"
        UPLOAD_FOLDER_BANNER = "apps/static/tempat_upload_foto/Foto_Banner"    
        # Memeriksa apakah ada file dalam request
        gambar_banner = request.files['gambar_banner']
        filepath_for_db = None 
        if 'gambar_banner' not in request.files:
            flash('Tidak ada gambar yang diunggah')
            return redirect(request.url)

        # Jika file valid dan diizinkan
        if gambar_banner and allowed_file(gambar_banner.filename):
            filename = secure_filename(gambar_banner.filename)
            filepath = os.path.join(UPLOAD_FOLDER_BANNER, filename)
            filepath_for_db = os.path.join(UPLOAD_FOLDER_DB_BANNER, filename).replace("\\", "/")
            print(filepath_for_db)
            gambar_banner.save(filepath)
            optimize_image_tinyjpg(filepath)
            # gambar_pengumuman.save(UPLOAD_FOLDER, filename)
           
            #  Membuat objek siswa baru
        gambar_banner_baru = Foto_Banner(img_banner_path=filepath_for_db )
  
        
            # Menyimpan ke database
        db.session.add(gambar_banner_baru)
        db.session.commit()
        return redirect(url_for('home_blueprint.admin_banner_photo'))
          
    return render_template('users_template/admin_tambah_banner.html', segment='admin')


@blueprint.route('/Admin/Admin_Banner/delete_banner<int:id_banner>' , methods=['GET', 'POST'])
@login_required
def admin_delete_banner(id_banner):
    foto_banner = Foto_Banner.query.get_or_404(id_banner) 
    db.session.delete(foto_banner)
    db.session.commit()
    return redirect(url_for('home_blueprint.admin_banner_photo'))


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'student'

        return segment

    except:
        return None
