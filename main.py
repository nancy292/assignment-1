from typing import Optional
from fastapi import FastAPI, Request,Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore

app = FastAPI()

firestore_db = firestore.Client()
firebase_request_adapter = requests.Request()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):

    return templates.TemplateResponse(
        "home.html",
         {"request": request}
    )

@app.get("/drivers",response_class=HTMLResponse)
def retrive_drivers(request:Request):
    query = firestore_db.collection('drivers')
    drivers = [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]
    return templates.TemplateResponse(
        "display_driver.html",
        {"drivers":drivers,
         "request": request}
    )

@app.get("/create/driver",response_class=HTMLResponse)
def register_drivers(request:Request):
    return templates.TemplateResponse(
            "create-driver.html",
            {"request": request}
        )


@app.post("/create/driver",response_class=HTMLResponse)
def register_drivers(request:Request,name=Form(...),age=Form(...),pole_positions=Form(...),race_wins=Form(...),
                  points_scored=Form(...),world_titles=Form(...),fastest_laps=Form(...),drive_team=Form(...)):
    driver_exists = firestore_db.collection('drivers').where(field_path='name', op_string='==', value=name).limit(1).get()
    if len(driver_exists) > 0:
        raise Exception("name already taken.Please use another name")
    if age < 0:
        raise Exception("age must be greater than 0 years old")
    if pole_positions < 0:
        raise Exception("pole positions must be greater or equal to  0")
    if race_wins < 0:
        raise Exception("race wins must be greater or equal to  0")
    if points_scored < 0:
        raise Exception("points scored must be greater or equal to  0")
    if world_titles < 0:
        raise Exception("world titles must be greater or equal to  0")
    if fastest_laps < 0:
        raise Exception("fastest laps must be greater or equal to  0")
    team_exist = firestore_db.collection('teams').where('name','==',drive_team).limit(1).get()
    if len(team_exist)<=0:
        raise Exception("create team name before assigning it to a driver")
    driver_data = {
        "name": name,
        "age": age,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "points_scored": points_scored,
        "world_titles": world_titles,
        "fastest_laps": fastest_laps,
        "drive_team": drive_team
    }
    firestore_db.collection('drivers').add(driver_data)
    return None

@app.post("create/teams",response_class=HTMLResponse)
def register_team(request:Request,name=Form(...),year_founded=Form(...),pole_positions=Form(...),race_wins=Form(...),
                constructor_titles=Form(...),prev_finish_position=Form(...)):
    team_exists = firestore_db.collection('teams').where('name', '==', name).limit(1).get() 
    if len(team_exists) > 0:
        raise Exception("name already taken.Please use another name")
    if year_founded < 1799 or year_founded>2025:
        raise Exception("Year must be greater than 1800 and less than 2025")
    if pole_positions < 0:
        raise Exception("total pole positions must be greater than zero")
    if race_wins < 0:
        raise Exception("Toatl race wins must be greater than zero")
    if constructor_titles < 0:
        raise Exception("Total constructor title must be greater than zero")
    if prev_finish_position < 0:
        raise Exception("previous season position must be greater than zero")
    
    team_data = {
        "name":name,
        "year_founded":year_founded,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "constructor_titles":constructor_titles,
        "prev_finish_position":prev_finish_position
    }
    firestore_db.collection('teams').add(team_data)
    return None
