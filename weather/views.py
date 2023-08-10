from django.shortcuts import render, redirect
import requests
from .models import City
from .forms import CityForm 


url = "http://api.weatherapi.com/v1/forecast.json?key=6a03284e2cbd4fabaf1171630222811&q={}&days=6&aqi=no&alerts=no"
img_api_url = "https://api.teleport.org/api/urban_areas/slug:{}/images/"

# Create your views here.
def index(request):
    global url
    
    err_mgs = ""
    message = ""
    message_class = ""
    
    if request.method == "POST":
        p = dict(request.POST)       
        pre_n = requests.get(url.format(p["name"])).json()     
        p["name"] = pre_n["location"]["name"]
        
        form = CityForm(p)
        
        # form = doan ma html the hien cai POST len server
        
        if form.is_valid():     # kiem tra form hop le k
            new_city = form.cleaned_data["name"] # ten thanh pho  
            
            existing_city_count = City.objects.filter(name=new_city).count()   # kiem tra thanh pho co bi trung khong
            
            if existing_city_count == 0: 
                r = requests.get(url.format(new_city)).json()       # lay data thoi tiet cua thanh pho dang json
                if "error" not in r: form.save()         # luu vao database
                    
                else: err_mgs = "City doesn't exist in the world"
            else: err_mgs = "City already exist in database"
        
        if err_mgs:
            message = err_mgs
            message_class = "is-danger"
            
        else:
            message = "Add successfully!"
            message_class = "is-success"
    
    
    form = CityForm()                   # form cho user nhap ten thanh pho
    cities = City.objects.all()            # list cac data tho
    weather_data = []                   # list du lieu thoi tiet tung thanh pho

    for city in cities:       
        r = requests.get(url.format(city)).json()

        city_weather = {
            "city": r["location"]["name"],
            "temperature": r["current"]["temp_c"],
            "description": r["current"]["condition"]["text"],
            "icon": r["current"]["condition"]["icon"],
        }
    
        weather_data.append(city_weather)
        
        
    # tao cac bien de su dung trong file html
    context_html = {
        "weather_data": weather_data,
        "form": form,
        "message": message,
        "message_class": message_class
    }
    
    return render(request, "weather/weather.html", context_html)

def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect("home")


def reformat_date(date):
    return "/".join(list(reversed(date.split("-"))))
     
     
def detail(request, city_name):
    global url, img_api_url

    r = requests.get(url.format(city_name)).json()
    
    city = r["location"]["name"] + ", " + r["location"]["country"]
    
    today = r["location"]["localtime"]
    today_time = reformat_date(today.split(" ")[0]) + " " + today.split(" ")[1]
    
    temp_c = r["current"]["temp_c"]
    
    forecast_date = r["forecast"]["forecastday"][1: ]
    for d in forecast_date:
        d["date"] = reformat_date(d["date"])[: -5]
        
        
    city_img = city_name.lower().replace(" ", "-")
    pho = dict(requests.get(img_api_url.format(city_img)).json())
    img_ = pho["photos"][0]["image"]["web"] if "status" not in pho else "https://images.unsplash.com/photo-1569429512518-44dad00e88db?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"
    

    context_html = {
        "r": r,
        "city": city,
        "time": today_time,
        "temp_c": temp_c,
        "forecast_date": forecast_date,
        "img_": img_
    }
    
    return render(request, "weather/detail.html", context_html)