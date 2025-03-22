from typing import Optional
from fastapi import FastAPI, Request,Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
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
def retrive_drivers(request:Request,
                  attribute: Optional[str] = None, 
                  operator: Optional[str] = None, 
                  value: Optional[str] = None):
    if attribute and operator and value:
        query = firestore_db.collection('drivers')
        try:
            if attribute not in ["name", "drive_team"]:
                value = int(value)
        except:
            raise Exception("Invalid input: Please enter valid numbers for numeric fields.")
        query = query.where(attribute, operator, value)
        drivers = [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]
        query_info = f"{attribute} {operator} {value}"
        return templates.TemplateResponse(
            "display_drivers.html",
            {"drivers":drivers,
             "query_info":query_info,
            "request": request}
        )
    else :
        query = firestore_db.collection('drivers')
        drivers = [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]
        return templates.TemplateResponse(
            "display_drivers.html",
            {"drivers":drivers,
            "request": request}
        )


@app.get("/drivers/{driver_id}",response_class=HTMLResponse)
def retrive_driver(request:Request,driver_id:str):
    driver = firestore_db.collection("drivers").document(driver_id)
    driver = driver.get()
    if not driver.exists:
        return HTMLResponse(content="not a valid driver id",status_code=303)
    driver_dict = {"id": driver.id, **driver.to_dict()}
    query = firestore_db.collection("teams")
    teams = [doc.to_dict() for doc in query.stream()]
    return templates.TemplateResponse(
        "create-driver.html",
        {"request": request, "driver": driver_dict, "teams": teams}
    )
    

@app.get("/create/driver",response_class=HTMLResponse)
def register_drivers(request:Request):
    query = firestore_db.collection('teams')
    teams = [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]
    return templates.TemplateResponse(
            "create-driver.html",
            {"request": request,
             "teams":teams,
             }
        )


@app.post("/create/driver", response_class=HTMLResponse)
def register_drivers(
    request: Request,
    name: str = Form(...),
    age: str = Form(...),
    pole_positions: str = Form(...),
    race_wins: str = Form(...),
    points_scored: str = Form(...),
    world_titles: str = Form(...),
    fastest_laps: str = Form(...),
    drive_team: str = Form(...)
):
    # Convert string inputs to integers
    try:
        age = int(age)
        pole_positions = int(pole_positions)
        race_wins = int(race_wins)
        points_scored = int(points_scored)
        world_titles = int(world_titles)
        fastest_laps = int(fastest_laps)
    except ValueError:
        raise Exception("Invalid input: Please enter valid numbers for numeric fields.")

    # Validation
    if age < 0:
        raise Exception("Age must be greater than 0 years old.")
    if pole_positions < 0:
        raise Exception("Pole positions must be 0 or greater.")
    if race_wins < 0:
        raise Exception("Race wins must be 0 or greater.")
    if points_scored < 0:
        raise Exception("Points scored must be 0 or greater.")
    if world_titles < 0:
        raise Exception("World titles must be 0 or greater.")
    if fastest_laps < 0:
        raise Exception("Fastest laps must be 0 or greater.")

    # Check if driver name already exists
    driver_exists = firestore_db.collection('drivers').where('name', '==', name).limit(1).get()
    if len(driver_exists) > 0:
        raise Exception("Name already taken. Please use another name.")

    # Check if the assigned team exists
    team_exist = firestore_db.collection('teams').where('name', '==', drive_team).limit(1).get()
    if len(team_exist) == 0:
        raise Exception("Create the team before assigning it to a driver.")

    # Save driver data
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

    return RedirectResponse(url="/drivers", status_code=303)

@app.post("/query/drivers",response_class=HTMLResponse)
def query_drivers(request:Request,
                attribute=Form(...),
                operator=Form(...),
                value=Form(...)):
    
    return RedirectResponse(
        url=f"/drivers?attribute={attribute}&operator={operator}&value={value}",
        status_code=303
    )



@app.post("/drivers/{driver_id}", response_class=HTMLResponse)
def register_drivers(
    request: Request,
    driver_id:str,
    age: str = Form(...),
    pole_positions: str = Form(...),
    race_wins: str = Form(...),
    points_scored: str = Form(...),
    world_titles: str = Form(...),
    fastest_laps: str = Form(...),
    drive_team: str = Form(...)
    ):
    try:
        age = int(age)
        pole_positions = int(pole_positions)
        race_wins = int(race_wins)
        points_scored = int(points_scored)
        world_titles = int(world_titles)
        fastest_laps = int(fastest_laps)
    except ValueError:
        raise Exception("Invalid input: Please enter valid numbers for numeric fields.")

    # Validation
    if age < 0:
        raise Exception("Age must be greater than 0 years old.")
    if pole_positions < 0:
        raise Exception("Pole positions must be 0 or greater.")
    if race_wins < 0:
        raise Exception("Race wins must be 0 or greater.")
    if points_scored < 0:
        raise Exception("Points scored must be 0 or greater.")
    if world_titles < 0:
        raise Exception("World titles must be 0 or greater.")
    if fastest_laps < 0:
        raise Exception("Fastest laps must be 0 or greater.")


    # Check if the assigned team exists
    team_exist = firestore_db.collection('teams').where('name', '==', drive_team).limit(1).get()
    if len(team_exist) == 0:
        raise Exception("Create the team before assigning it to a driver.")

    # Save driver data
    driver_data = {
        "age": age,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "points_scored": points_scored,
        "world_titles": world_titles,
        "fastest_laps": fastest_laps,
        "drive_team": drive_team
    }
    ref = firestore_db.collection("drivers").document(driver_id)
    if not ref.get().exists:
        raise Exception("Team not found")
    ref.update(driver_data)
    return RedirectResponse(url="/drivers", status_code=303)

@app.delete("/drivers/{driver_id}",response_class=HTMLResponse)
def delete_driver(request:Request,driver_id:str):
    ref = firestore_db.collection("drivers").document(driver_id)
    if not ref.get().exists:
        raise Exception("Driver not found")
    ref.delete()
    return RedirectResponse(url="/drivers", status_code=303)








@app.get("/teams",response_class=HTMLResponse)
def retrive_teams(request:Request,
                  attribute: Optional[str] = None, 
                  operator: Optional[str] = None, 
                  value: Optional[str] = None):
    if attribute and operator and value:
        query = firestore_db.collection('teams')
        try:
            if not attribute == 'name':
                value = int(value)
        except:
            raise Exception("Invalid input: Please enter valid numbers for numeric fields.")
        query = query.where(attribute, operator, value)
        teams = [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]
        query_info = f"{attribute} {operator} {value}"
        return templates.TemplateResponse(
            "display_teams.html",
            {"teams":teams,
             "query_info":query_info,
            "request": request}
        )
    else :
        query = firestore_db.collection('teams')
        teams = [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]
        return templates.TemplateResponse(
            "display_teams.html",
            {"teams":teams,
            "request": request}
        )


@app.get("/teams/{team_id}",response_class=HTMLResponse)
def retrive_driver(request:Request,team_id:str):
    team = firestore_db.collection("teams").document(team_id)
    team = team.get()
    if not team.exists:
        return HTMLResponse(content="not a valid team id",status_code=303)
    team_dict = {"id": team.id, **team.to_dict()}
    return templates.TemplateResponse(
        "create-team.html",
        {"request": request, "team": team_dict}
    )

@app.post("/teams/{team_id}",response_class=HTMLResponse)
def update_team(request:Request,
                team_id:str,
                year_founded: str = Form(...),
                pole_positions: str = Form(...),
                race_wins: str = Form(...),
                constructor_titles: str = Form(...),
                prev_finish_position: str = Form(...)):
    try:
        year_founded = int(year_founded)
        pole_positions = int(pole_positions)
        race_wins = int(race_wins)
        constructor_titles = int(constructor_titles)
        prev_finish_position = int(prev_finish_position)
    except ValueError:
        raise Exception("Invalid input: Please enter valid numbers for numeric fields.")

    if year_founded < 1800 or year_founded > 2025:
        raise Exception("Year must be between 1800 and 2025.")
    if pole_positions < 0:
        raise Exception("Total pole positions must be 0 or greater.")
    if race_wins < 0:
        raise Exception("Total race wins must be 0 or greater.")
    if constructor_titles < 0:
        raise Exception("Total constructor titles must be 0 or greater.")
    if prev_finish_position < 1:
        raise Exception("Previous season position must be at least 1.")

    ref = firestore_db.collection("teams").document(team_id)
    if not ref.get().exists:
        raise Exception("Team not found")
    team_data = {
        
        "year_founded": year_founded,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "constructor_titles": constructor_titles,
        "prev_finish_position": prev_finish_position
    }
    ref = firestore_db.collection("teams").document(team_id)
    ref.update(team_data)

    return RedirectResponse(url="/teams", status_code=303)
    

@app.get("/create/team",response_class=HTMLResponse)
def register_team(request:Request):
    return templates.TemplateResponse(
            "create-team.html",
            {"request": request}
        )

@app.post("/create/team", response_class=HTMLResponse)
def register_team(
    request: Request,
    name: str = Form(...),
    year_founded: str = Form(...),
    pole_positions: str = Form(...),
    race_wins: str = Form(...),
    constructor_titles: str = Form(...),
    prev_finish_position: str = Form(...)
):
    
    try:
        year_founded = int(year_founded)
        pole_positions = int(pole_positions)
        race_wins = int(race_wins)
        constructor_titles = int(constructor_titles)
        prev_finish_position = int(prev_finish_position)
    except ValueError:
        raise Exception("Invalid input: Please enter valid numbers for numeric fields.")

    
    if year_founded < 1800 or year_founded > 2025:
        raise Exception("Year must be between 1800 and 2025.")
    if pole_positions < 0:
        raise Exception("Total pole positions must be 0 or greater.")
    if race_wins < 0:
        raise Exception("Total race wins must be 0 or greater.")
    if constructor_titles < 0:
        raise Exception("Total constructor titles must be 0 or greater.")
    if prev_finish_position < 1:
        raise Exception("Previous season position must be at least 1.")

    
    team_data = {
        "name": name,
        "year_founded": year_founded,
        "pole_positions": pole_positions,
        "race_wins": race_wins,
        "constructor_titles": constructor_titles,
        "prev_finish_position": prev_finish_position
    }
    firestore_db.collection('teams').add(team_data)

    return RedirectResponse(url="/teams", status_code=303)


@app.post("/query/teams",response_class=HTMLResponse)
def query_teams(request:Request,
                attribute=Form(...),
                operator=Form(...),
                value=Form(...)):
    
    return RedirectResponse(
        url=f"/teams?attribute={attribute}&operator={operator}&value={value}",
        status_code=303
    )


@app.delete("/teams/{team_id}",response_class=HTMLResponse)
def delete_team(request:Request,team_id:str):
    ref = firestore_db.collection("teams").document(team_id)
    if not ref.get().exists:
        raise Exception("Team not found")
    ref.delete()
    return RedirectResponse(url="/teams", status_code=303)