# main.py

from typing import Optional
from collections import defaultdict
from fastapi import FastAPI
from pydantic import BaseModel, conlist
import which_plates

class PlateRequest(BaseModel):
    bar_weight: int
    rep_max:  int
    available_plates: conlist(float)
    percentages: conlist(int)

class Plate(BaseModel):
    weight: float
    count: int

class Set(BaseModel):
    total_weight: float
    plate_weight: float
    percentage: int
    count: int
    plates:  list[Plate]


class PlateResponse(BaseModel):
    used_plates: list[Plate]
    sets: list[Set]

app = FastAPI()

@app.post("/calculate/", response_model=PlateResponse)
async def calculate_plates(plate_request: PlateRequest) -> PlateResponse:
    
    
    set_count = 1
    used_plates = {}
    sets = []

    plate_request.available_plates.sort(reverse=True)
    for plates in plate_request.available_plates:
        used_plates[plates] = 0

    for percent in plate_request.percentages:

        # calculate plate weight needed for current percentage
        plate_weight = which_plates.round_num((plate_request.rep_max * percent/100) - plate_request.bar_weight)

        if plate_weight <= 0:
            #TODO error
            print("    Computed weight less than bar weight, try again")
        else:


            # calculate required plates for set
            plates = which_plates.calc_plates(plate_weight, plate_request.available_plates)
            current_set_plates=[]
            for p_weight, p_count in plates.items():
                current_set_plates.append({
                    'weight': p_weight,
                    'count': p_count
                })
                if used_plates[p_weight] < p_count:
                    used_plates[p_weight] = p_count


            sets.append({
                'total_weight': round(plate_weight + plate_request.bar_weight),
                'plate_weight': round(plate_weight),
                'percentage': percent,
                'count': set_count,               
                'plates': current_set_plates
            })

            set_count += 1
    
    final_plates = []
    for weight, count in used_plates.items():
        final_plates.append({
            'weight': weight,
            'count': count
            }
        )
    result = {'used_plates': final_plates, 'sets': sets}
    return(result)
