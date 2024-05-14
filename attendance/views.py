from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .models import Student, Log
from django.shortcuts import redirect
import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

global stat
stat = ''
# Create your views here.
global selected
selected = None


def index1(request):
    logs = Log.objects.all().order_by('date')  # Sắp xếp các đối tượng Log theo thứ tự từ mới nhất đến cũ nhất
    dataset = {'log': logs}
    return render(request, 'attendance/attendance.html', dataset)



def index(request):
    logs = Log.objects.order_by('date')  # Sắp xếp theo thời gian vào
    return render(request, 'attendance/index.html', {'logs': logs})

def process(request):
	card = request.GET.get('card_id', None)
	users = Student.objects.all()
	for user in users:
		if user.card_id == int(card):
			ans = attend(user)
			channel_layer = get_channel_layer()
			async_to_sync(channel_layer.group_send)(
        'notifications',  # Tên nhóm (group) để gửi thông báo
        {
            'type': 'send_notification',  # Loại thông báo
            'message': "ghiihihih"  # Nội dung thông báo
        }
    )

			return HttpResponse(ans)

	new_student = Student(card_id=card)
	new_student.save()
	return HttpResponse('Dữ liệu trống đã tiến hành đăng ký CardID')

def attend(user):
	status =[]
	if user.name is None:
		return 'Vui lòng liên hệ quản trị viên để cập nhật thông tin'
	logs = Log.objects.filter(card_id=user.card_id).order_by('-ida')
	
	if len(logs) == 0:
		size_Log = Log.objects.count()
		new_log, created = Log.objects.update_or_create(
    			card_id=user.card_id,
    			date=datetime.datetime.now().date(),
				time_in=datetime.datetime.now(),
				defaults={
					'ida': size_Log,
					'name': user.name,
					'phone': user.phone,
					'masv': user.masv,
					'time_out': None,
				}
			)	
		status =['check in',user]
	else:
		first_log = logs.first()
		if first_log.time_out is None:
			first_log.time_out = datetime.datetime.now()
			first_log.save()
			status =['check out',user]
		else:
			size_Log = Log.objects.count()
			new_log, created = Log.objects.update_or_create(
    			card_id=user.card_id,
    			date=datetime.datetime.now().date(),
				time_in=datetime.datetime.now(),
				defaults={
					'ida': size_Log,
					'name': user.name,
					'phone': user.phone,
					'masv': user.masv,
					'time_out': None,
				}
			)
			status =['check in',user]			


	return status






def details1(request):
    users = Student.objects.all().order_by('id')
    userset = {'users': users}
    return render(request, 'attendance/userdetails.html', userset)


def details(request):
	return render(request, 'attendance/details.html')


def manage1(request):
    users = Student.objects.all().order_by('id')
    userset = {'users': users}
    global stat
    stat = ''
    return render(request, 'attendance/allusers.html', userset)

def manage(request):
    users = Student.objects.all().order_by('id')
    context = {'users': users} 
    return render(request, 'attendance/manage.html', context)


def card(request):
	sel_user = ''
	users = Student.objects.all().order_by('id')
	global stat
	global selected
	if request.method == 'POST':
		if request.POST.get("sel"):
			ids = request.POST.get('idsearch', 'kuch nahi mila')
			for user in users:
				if user.card_id == int(ids):
					stat = 'Card is Selected'
					selected = user
					break
				else:
					stat = 'Card not found'
			return redirect('/manage')
		else:
			ids = request.POST.get('idsearch')
			if Student.objects.filter(card_id=int(ids)).exists():
				Student.objects.filter(card_id=int(ids)).delete()
				Log.objects.filter(card_id=int(ids)).delete()

				stat = 'Deleted Successfully'
			else:
				stat = 'Card not found'
			return redirect('/manage')

def add(request):
    # Lấy thông tin từ request POST
    name = request.POST.get('name')
    card_id = request.POST.get('card_id')
    masv = request.POST.get('masv')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    birth_date = request.POST.get('birth_date')
    sex = request.POST.get('sex')
    
    # Kiểm tra xem các trường dữ liệu cần thiết đã được điền đầy đủ chưa
    if not all([name, card_id, masv, phone, email, birth_date, sex]):
        return HttpResponseBadRequest('Vui lòng điền đầy đủ thông tin.')
    
    # Kiểm tra xem trường birth_date có được nhập không
    if not birth_date:
        return HttpResponseBadRequest('Vui lòng nhập ngày sinh.')
    
    # Tạo một đối tượng Student mới và lưu vào cơ sở dữ liệu
    new_student = Student(
        name=name,
        card_id=card_id,
        masv=masv,
        phone=phone,
        email=email,
        birth_date=birth_date,
        sex=sex
    )
    new_student.save()
    
    # Chuyển hướng người dùng đến một trang hoặc URL khác sau khi thêm thành công
    return redirect('/manage')
	
def edit(request):
  
    student = get_object_or_404(Student, card_id=request.POST.get('card_id'))

   
    student.name = request.POST.get('name')
    student.masv = request.POST.get('masv')
    student.phone = request.POST.get('phone')
    student.email = request.POST.get('email')
    student.birth_date = request.POST.get('birth_date')
    student.sex = request.POST.get('sex')
    
   
    student.save()
    
   
    return redirect('/manage')

def search(request):
	sel_user = ''
	users = Student.objects.all()
	logs = Log.objects.all()
	path = request.get_full_path()
	card_id = request.POST.get('search').strip() if request.POST.get('search') else None

	logf = []
	for user in users:
		if str(user.card_id) == str(card_id):
			sel_user = user
	logf = Log.objects.filter(card_id=card_id)

		
	dataset = {'use': sel_user, 'log': logf}
	return render(request, 'attendance/search.html', dataset)




def delete(request,pk):
    
	Student.objects.filter(card_id=pk).delete()

	return HttpResponse('xoas ok')

    
def CardUidDetailApiView(request, pk):
	student = get_object_or_404(Student, card_id=pk)
	return JsonResponse({
			'id': student.id,
			'name': student.name,
			'card_id': student.card_id,
			'phone': student.phone,
			'masv': student.masv,
			'sex': student.sex,
			'email':student.email,
			'birth_date':student.birth_date
			
		})