from apps import db
from datetime import date
from flask_login import UserMixin

class Users(db.Model, UserMixin):

    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    is_active = db.Column(db.Boolean,  default=False)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Siswa_Baru(db.Model):
    __tablename__ = 'tbl_siswa_baru'
    id_siswa_baru = db.Column(db.Integer, primary_key=True)
    nomor_identitas = db.Column(db.String(255),nullable=False)
    nama_siswa_baru = db.Column(db.String(255), nullable=False)


    def __repr__(self):
        return f'<siswa {self.nomor_identitas}>'
    



class Siswa(db.Model):
    __tablename__ = 'tb_siswa'

    nama = db.Column(db.String(128), nullable=False)
    nipd = db.Column(db.String(64), nullable=False)
    jk = db.Column(db.String(1), nullable=False)
    nisn = db.Column(db.String(64), primary_key=True, nullable=False)
    tempat_lahir = db.Column(db.String(256), nullable=False)
    tanggal_lahir = db.Column(db.String(16), nullable=False)
    nik = db.Column(db.String(64), nullable=False)
    agama = db.Column(db.String(16), nullable=False)
    alamat = db.Column(db.String(256), nullable=False)
    rt = db.Column(db.String(3), nullable=True)
    rw = db.Column(db.String(3), nullable=True)
    dusun = db.Column(db.String(64), nullable=True)
    kelurahan = db.Column(db.String(64), nullable=True)
    kecamatan = db.Column(db.String(64), nullable=True)  # Mungkin seharusnya 'kecamatan'
    kode_pos = db.Column(db.String(16), nullable=True)
    jenis_tinggal = db.Column(db.String(64), nullable=False)
    alat_transportasi = db.Column(db.String(64), nullable=True)
    no_hp = db.Column(db.String(32), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    skhun = db.Column(db.String(128), nullable=True)
    penerima_kps = db.Column(db.String(32), nullable=True)
    no_kps = db.Column(db.String(128), nullable=True)
    nama_ayah = db.Column(db.String(128), nullable=True)
    tahun_lahir_ayah = db.Column(db.Integer,nullable=True)
    jenjang_pendidikan_ayah = db.Column(db.String(50), nullable=True)
    pekerjaan_ayah = db.Column(db.String(50), nullable=True)
    penghasilan_ayah = db.Column(db.String(50), nullable=True)
    nik_ayah = db.Column(db.String(64),nullable=True)
    nama_ibu = db.Column(db.String(128), nullable=True)
    tahun_lahir_ibu =db.Column(db.Integer,nullable=True)
    jenjang_pendidikan_ibu = db.Column(db.String(50), nullable=True)
    pekerjaan_ibu = db.Column(db.String(50), nullable=True)
    penghasilan_ibu  = db.Column(db.String(50), nullable=True)
    nik_ibu = db.Column(db.String(64),nullable=True)
    nama_wali = db.Column(db.String(128), nullable=True)
    tahun_lahir_wali =db.Column(db.Integer,nullable=True)
    jenjang_pendidikan_wali = db.Column(db.String(50), nullable=True)
    pekerjaan_wali = db.Column(db.String(50), nullable=True)
    penghasilan_wali  = db.Column(db.String(50), nullable=True)
    nik_wali = db.Column(db.String(64),nullable=True)
    kelas = db.Column(db.Integer,db.ForeignKey('tbl_kelas.id_kelas'), nullable=True)
    for_kelas = db.relationship('Kelas', backref=db.backref('tbl_siswa', lazy=True))
    no_peserta_ujian_nasional = db.Column(db.String(128), nullable=True)
    no_seri_ijazah = db.Column(db.String(128), nullable=True)
    penerima_kip = db.Column(db.String(32), nullable=True)
    nomor_kip = db.Column(db.String(128), nullable=True)
    nama_kip = db.Column(db.String(128), nullable=True)
    nomor_kks = db.Column(db.String(128), nullable=True)
    noreg_akta_lahir = db.Column(db.String(128), nullable=True)
    bank = db.Column(db.String(64), nullable=True)
    no_rek_bank = db.Column(db.String(64), nullable=True)
    nama_rek_bank = db.Column(db.String(128), nullable=True)
    layak_pip = db.Column(db.String(32), nullable=True)
    alasan_layak_pip = db.Column(db.String(128), nullable=True)
    kebutuhan_khusus = db.Column(db.String(64), nullable=True)
    sekolah_asal = db.Column(db.String(128), nullable=True)
    anak_ke = db.Column(db.String(2), nullable=True)
    lintang = db.Column(db.Float, nullable=True)
    bujur = db.Column(db.Float, nullable=True)
    no_kk = db.Column(db.String(128), nullable=True)
    berat_badan = db.Column(db.String(4), nullable=True)
    tinggi_badan = db.Column(db.String(4), nullable=True)
    lingkar_kepala = db.Column(db.String(4), nullable=True)
    jml_saudara = db.Column(db.String(2), nullable=True)
    jarak_rumah_sekolah = db.Column(db.String(2), nullable=True)

    def __repr__(self):
        return f'<Siswa {self.nama}>'


    
class Kelas(db.Model):
    __tablename__ = 'tbl_kelas'
    id_kelas = db.Column(db.Integer, primary_key=True)
    nama_kelas = db.Column(db.String(10), nullable=False)
    id_wali_kelas = db.Column(db.Integer,db.ForeignKey('tb_guru.id_guru'), nullable=False)
    for_walas = db.relationship('Guru', backref=db.backref('tbl_kelas', lazy=True))

    # Untuk mencetak nama kelas dengan mudah
    def __repr__(self):
        return f'<Kelas {self.nama_kelas}>'
        

class Kelas_Jadwal(db.Model):
    __tablename__ = 'tbl_kelas_for_jadwal'
    id_kelas_jadwal = db.Column(db.Integer, primary_key=True)
    nama_kelas_jadwal = db.Column(db.String(10), nullable=False)
    

    # Untuk mencetak nama kelas dengan mudah
    def __repr__(self):
        return f'<Kelas {self.nama_kelas_jadwal}>'
    

# class Guru(db.Model):
#     __tablename__ = 'tbl_kepegawaian'
#     id_kepegawaian = db.Column(db.Integer, primary_key=True)
#     nip = db.Column(db.String(50), nullable=False)
#     nama_pegawai = db.Column(db.String(100), nullable=False)
#     kelahiran = db.Column(db.String(150), nullable=False)
#     image_guru_path = db.Column(db.String(255), nullable=True)
#     jk = db.Column(db.String(1), nullable=False)
#     status = db.Column(db.String(50), nullable=False)

#     # Untuk mencetak nama kelas dengan mudah
#     def __repr__(self):
#         return f'<Guru {self.nama_pegawai}>'

class Guru(db.Model):
    __tablename__ = 'tb_guru'
    id_guru = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(128), nullable=True)
    nip = db.Column(db.String(64), nullable=True)
    jk = db.Column(db.String(1), nullable=True)  # Menggunakan varchar(1) untuk jk
    tempat_lahir = db.Column(db.String(64), nullable=True)
    tanggal_lahir = db.Column(db.String(32), nullable=True)
    agama = db.Column(db.String(16), nullable=True)
    status = db.Column(db.String(32), nullable=True)
    golongan = db.Column(db.String(128), nullable=True)
    status_perkawinan = db.Column(db.String(128), nullable=True)
    jml_anak = db.Column(db.String(2), nullable=True)
    masa_kerja_thn = db.Column(db.String(12), nullable=True)
    masa_kerja_bln = db.Column(db.String(12), nullable=True)
    tmt_sd = db.Column(db.String(32), nullable=True)
    pendidikan = db.Column(db.String(64), nullable=True)
    jurusan = db.Column(db.String(64), nullable=True)
    lulus = db.Column(db.String(64), nullable=True)
    kelas_ajar = db.Column(db.String(16), nullable=True)
    jam_week = db.Column(db.String(3), nullable=True)
    image_path_guru = db.Column(db.String(255), nullable=True)

    # Untuk mencetak nama kelas dengan mudah
    def __repr__(self):
        return f'<Guru {self.nama}>'

    
class Acara_Kegiatan(db.Model):
    __tablename__ = 'tbl_kegiatan'
    id_kegiatan = db.Column(db.Integer, primary_key=True)
    nama_kegiatan = db.Column(db.String(50), nullable=False)
    konten_kegiatan = db.Column(db.String(1000), nullable=False)
    img_path_kegiatan = db.Column(db.String(255), nullable=True)
    tanggal_kegiatan = db.Column(db.Date, nullable=True)
   
    # Untuk mencetak nama kelas dengan mudah
    def __repr__(self):
        return f'<Kegiatan{self.nama_kegiatan}>'    

class Mata_Pelajaran(db.Model):
    __tablename__ = 'tbl_mata_pelajaran'
    id_mata_pelajaran = db.Column(db.Integer, primary_key=True)
    nama_mata_pelajaran = db.Column(db.String(50), nullable=False)

    # Untuk mencetak nama kelas dengan mudah
    def __repr__(self):
        return f'<Kelas {self.nama_mata_pelajaran}>'

class Kalender_Akademik(db.Model):
    __tablename__ = 'tbl_kalender_akademik'
    id_kegiatan = db.Column(db.Integer, primary_key=True)
    Kegiatan = db.Column(db.String(100), nullable=False)
    Tanggal_mulai      = db.Column(db.Date, nullable=False)
    Tanggal_selesai      = db.Column(db.Date, nullable=False)


    def __repr__(self):
        return f'<siswa {self.Kegiatan}>'



class Pengumuman(db.Model):
    __tablename__ = 'tbl_pengumuman'
    id_pengumuman = db.Column(db.Integer, primary_key=True)
    judul_pengumuman = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    isi     = db.Column(db.Text, nullable=False)
    tanggal = db.Column(db.Date, nullable=False)



    def __repr__(self):
        return f'<siswa {self.judul}>'
    

class Jadwal_Pelajaran(db.Model):
    __tablename__ = 'tbl_jadwal_pelajaran'
    id_jadwal = db.Column(db.Integer, primary_key=True)
    id_kelas = db.Column(db.String(10),db.ForeignKey('tbl_kelas.id_kelas'), nullable=True)
    hari = db.Column(db.String(10), nullable=False)
    jam_mulai = db.Column(db.Time, nullable=False)
    jam_selesai = db.Column(db.Time, nullable=False)
    mata_pelajaran = db.Column(db.String(50),db.ForeignKey('tbl_mata_pelajaran.id_mata_pelajaran'), nullable=False)
    for_kelas = db.relationship('Kelas', backref=db.backref('tbl_jadwal_pelajaran', lazy=True))
    for_matpel = db.relationship('Mata_Pelajaran', backref=db.backref('tbl_jadwal_pelajaran', lazy=True))
    


    def __repr__(self):
        return f'<jadwal {self.jadwal_pelajaran}>'


class Jadwal_Ujian(db.Model):
    __tablename__ = 'tbl_jadwal_ujian'
    id_jadwal_ujian = db.Column(db.Integer, primary_key=True)
    kelas = db.Column(db.Integer,db.ForeignKey('tbl_kelas_for_jadwal.id_kelas_jadwal'), nullable=False)
    hari = db.Column(db.String(10), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    mata_pelajaran = db.Column(db.Integer,db.ForeignKey('tbl_mata_pelajaran.id_mata_pelajaran'), nullable=False)
    pengawas =  db.Column(db.Integer,db.ForeignKey('tb_guru.id_guru'), nullable=False)
    keterangan = db.Column(db.String(255), nullable=True)
    
      

    foreign_kelas = db.relationship('Kelas_Jadwal', backref=db.backref('tbl_jadwal_ujian', lazy=True))
    for_matpel = db.relationship('Mata_Pelajaran', backref=db.backref('tbl_jadwal_ujian', lazy=True))
    for_guru = db.relationship('Guru', backref=db.backref('tbl_jadwal_ujian', lazy=True))
    


    def __repr__(self):
        return f'<jadwal {self.id_jadwal_ujian}>'


class Profil_Sekolah(db.Model):
    __tablename__ = 'tbl_profil_sekolah'

    id_sekolah = db.Column(db.Integer, primary_key=True)
    nama_sklh = db.Column(db.String(50))
    nis = db.Column(db.String(30))      
    nss = db.Column(db.String(30))
    provinsi = db.Column(db.String(50))
    otonomi = db.Column(db.String(50))
    kecamatan = db.Column(db.String(50))
    desa_kelurahan = db.Column(db.String(50))
    jln_no = db.Column(db.String(50))
    kode_pos = db.Column(db.String(10))
    telepon = db.Column(db.String(15))
    faximile = db.Column(db.String(15))
    daerah = db.Column(db.String(20))
    status_sklh = db.Column(db.String(20))
    kelompok_sklh = db.Column(db.String(20))
    akreditasi = db.Column(db.String(1))
    surat_keputusan_sk = db.Column(db.String(100))
    tanggal_sk = db.Column(db.String(50))
    penerbit_sk = db.Column(db.String(100))
    thn_berdiri = db.Column(db.String(10))
    thn_perubahan = db.Column(db.String(10))
    kegiatan_bljr_mengajar = db.Column(db.String(50))
    bangunan_sklh = db.Column(db.String(20))
    luas_bangunan = db.Column(db.String(10))
    lokasi_sklh = db.Column(db.String(20))
    jarak_kecamatan = db.Column(db.String(10))
    jarak_otoda = db.Column(db.String(10))
    terletak_pd_lintasan = db.Column(db.String(30))
    jmlh_keanggotaan_gugus = db.Column(db.String(20))
    organisasi_penyelenggara = db.Column(db.String(20))
    perjalanan_perubahan_sklh = db.Column(db.String(50))

    def __repr__(self):
        return f'<jadwal {self.nama_sklh}>'
    
class Fasilitas_Sekolah(db.Model):
    __tablename__ = 'tbl_fasilitas'

    id_fasilitas = db.Column(db.Integer, primary_key=True)
    nama_fasilitas = db.Column(db.String(255))
    gambar_fasilitas = db.Column(db.String(50))      
    
    def __repr__(self):
        return f'<jadwal {self.nama_fasilitas}>'

from sqlalchemy import CheckConstraint

# class Setting(db.Model):
#     __tablename__ = 'tbl_setting'

#     id_setting = db.Column(db.Integer, primary_key=True)
#     semester = db.Column(db.String(50))
#     tahun_ajaran = db.Column(db.String(50))
#     siswa_baru =  db.Column(db.SmallInteger, CheckConstraint('siswa_baru IN (0, 1)'), default=False) 
#     assesment_sumatif   = db.Column(db.String(50))
    
#     def __repr__(self):
#         return f'<jadwal {self.id_setting}>'

class Setting(db.Model):
    __tablename__ = 'tbl_setting'

    id_setting = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(50))
    tahun_ajaran = db.Column(db.String(50))
    siswa_baru = db.Column(db.SmallInteger, CheckConstraint('siswa_baru IN (0, 1)'), default=0)  # Default 0 untuk siswa baru yang belum terdaftar
    assesment_sumatif = db.Column(db.String(50))

    def __repr__(self):
        return f'<Setting {self.id_setting}>'


class Foto_Banner(db.Model):
    __tablename__ = 'tbl_foto_banner'

    id_photo = db.Column(db.Integer, primary_key=True)
    img_banner_path = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<jadwal {self.id_photo}>'