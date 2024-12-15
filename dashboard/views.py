from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
import os # Import Q for complex queries
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json 
import logging
from datetime import datetime
from django.utils.timezone import now
logger = logging.getLogger(__name__)

from datetime import timedelta

import requests


Logged_id=None

@login_required
def get_user_info(request):


    global Logged_id
    user = request.user
    id = {(user.get_short_name()).split(' ')[0]}
    Logged_id = str(id).replace('-', '').replace('{', '').replace('}', '').replace("'", '').replace('"', '').strip()
  
    initials=user.username.split('.')[0][0].upper()  + user.username.split('.')[1].split('@')[0][0].upper() 
    print(initials)
    if os.path.exists(f'static/initials/{initials}.jpg'):
        print('profile exist')
    else:

        create_profile_image(initials, f'{initials}.jpg')
    user_info = {
        'username': user.username,
        'email': user.email,
        'id' : id,
        'lastname' : user.last_name,
        'initials': initials,
        
    }
    return user_info



def main(request):
    user_info=get_user_info(request)
    global Logged_id

    # admins(request) just to register email as admin
    return render(request, 'dashboard_templates/dashboard_main.html', {
        **get_user_info(request)  # Assuming this returns a dictionary
    })
from datetime import datetime, timezone

def votes(request):

    user_info = get_user_info(request)
    global Logged_id
    current_time = datetime.now(timezone.utc)  # Ensure current_time is offset-aware
    # current_time=current_time + timedelta(hours=8) 
    is_future_ctr=0
    
    api_url = "http://localhost:5196/api/elections"
    try:
    
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()  # Parse JSON data
        elections = data.get("result", [])
        for election in elections:
            # Ensure the required keys exist and process dates
            open_date = datetime.fromisoformat(election['openDate'].replace('Z', '+00:00'))
            close_date = datetime.fromisoformat(election['closeDate'].replace('Z', '+00:00'))
            if open_date.tzinfo is None:
                open_date = open_date.replace(tzinfo=timezone.utc)
            if close_date.tzinfo is None:
                close_date = close_date.replace(tzinfo=timezone.utc)
            election['open_date']=open_date
            election['close_date']=close_date
          
            election['is_future'] = open_date > current_time
            election['is_close'] = close_date < current_time
            election['is_present'] = open_date <= current_time <= close_date

          

            if(election['is_future']):
                is_future_ctr+=1
                
    except requests.exceptions.RequestException as e:
   
        total_users = pending_orders = completed_orders = active_vendors = inactive_vendors = 0


    context = {
        'elections': elections,
        'is_future_ctr': is_future_ctr
    }
   
    return render(request, 'dashboard_templates/dashboard_votes.html', context | get_user_info(request=request))

def votes_candidates(request, election_id):
    candidate_by_election = f"http://localhost:5196/api/Candidates/election/{election_id}"
    election_by_id = f"http://localhost:5196/api/Elections/{election_id}"
    position_by_election = f"http://localhost:5196/api/Positions/election/{election_id}"
    position_by_election = f"http://localhost:5196/api/Positions/election/{election_id}"
    
    vote_slip = ''
    isDisabled= ''  
    voted_candidate_ids=''  
 

    # Filter candidates based on the current election and search query
    try:
      
      
        response = requests.get(candidate_by_election)
        response.raise_for_status()  
        data = response.json() 
        candidates = data
        disabled=''
        response=None
        response = requests.get(election_by_id)
        response.raise_for_status()  
        data = response.json() 
        election = data

        import pytz
       
        current_time = datetime.now(timezone.utc)

       
        closeDate_time = datetime.strptime(election['closeDate'], "%Y-%m-%dT%H:%M:%S")

        # Localize closeDate_time to UTC (making it aware)
        closeDate_time_utc = pytz.utc.localize(closeDate_time)
        print(f'{current_time}   {closeDate_time_utc}')
      
        if current_time > closeDate_time_utc:
            isDisabled = 'disabled'
        print(disabled)

      
        
        response=None
        response = requests.get(position_by_election)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()  # Parse JSON data
        positions = data

        for position in positions:
            position['has_candidates']=False
            for canidate in candidates:
                if canidate['positionId'] == position['id'] :
                    position['has_candidates']=True
    
        open_date = datetime.fromisoformat(election['openDate'].replace('Z', '+00:00'))
        close_date = datetime.fromisoformat(election['closeDate'].replace('Z', '+00:00'))
        if open_date.tzinfo is None:
            open_date = open_date.replace(tzinfo=timezone.utc)
        if close_date.tzinfo is None:
            close_date = close_date.replace(tzinfo=timezone.utc)
        election['open_date']=open_date
        election['close_date']=close_date

  
        
    except requests.exceptions.RequestException as e:
        # Handle API errors
        print(f"Error fetching data from API: {e}")
    global Logged_id
    get_user_info(request=request)
    voteslip_by_student_election_id = f'http://localhost:5196/api/VoteSlips/student/{Logged_id}/election/{election_id}'
    response = requests.get(voteslip_by_student_election_id)
    

    try:
        response.raise_for_status()
        data = response.json()  
        
        data = data  
        voted_candidate_ids=data[0]['candidateIds']
        print(data[0]['candidateIds'])
     
        if data:  
            isDisabled = 'disabled'
        else:
            isDisabled = ''  

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
       
    

    context = {
            'election': election,
            'positions': positions,
            'candidates': candidates,
            'disabled' : isDisabled,
            'voted_ids': voted_candidate_ids  
        }
    
    return render(request, 'dashboard_templates/dashboard_votes_candidates.html',  context|get_user_info(request))
   

def get_positions(request, election_id):
    # positions = Position.objects.filter(election_id=election_id)
    # positions_data = [{"id": position.id, "title": position.title} for position in positions]
    # return JsonResponse({"positions": positions_data})
    print()

def guidelines(request):
    return render(request, 'dashboard_templates/dashboard_guidelines.html', get_user_info(request))

def logout(request):
    auth_logout(request)  # Logs the user out
    return redirect('home')  # Redirects to the main dashboard view


@csrf_exempt
@require_POST
def submit_votes(request):
    try:
        
        # Parse the JSON data from the request body
        data = json.loads(request.body)
            
        # Extract votes and election_id
        votes = data.get('votes', [])
        
        election_id = votes[0].get('election_id')
        
        
        if not votes:
            return JsonResponse({'success': False, 'error': 'No votes provided'})

        if not election_id:
            return JsonResponse({'success': False, 'error': 'Election ID missing'})
        
        for vote in votes:
            candidate_id_list = vote.get('candidate_id')
            position_list = vote.get('position')

            if not candidate_id_list or not position_list:
                return JsonResponse({'success': False, 'error': 'Invalid vote format'})

            n = len(candidate_id_list)
            for i in range(n):
                candidate_id = candidate_id_list[i]
                position = position_list[i]

                if not candidate_id:
                    return JsonResponse({'success': False, 'error': 'Candidate ID missing in vote'})
                if not position:
                    return JsonResponse({'success': False, 'error': 'Position missing in vote'})

                # Fetch the candidate from the database
                try:
                    candidate_url = f"http://localhost:5196/api/Candidates/{candidate_id}"
                    response = requests.get(candidate_url)
                    response.raise_for_status()
                   
                    candidate_data = response.json()
                    candidate_data['voteCount'] += 1

                    update_response = requests.put(candidate_url, json=candidate_data)
                   
                    update_response.raise_for_status()
                    print('succesfully incremented')
                   
                 
                except requests.RequestException:
                    return JsonResponse({'success': False, 'error': f'Failed to update candidate with ID {candidate_id}'})

        # Create a voteslip
        create_voteslip_url = "http://localhost:5196/api/Voteslips"
        student = getStudentLoggedIn(request=request)
        
        voteslip_data = {
        "studentId": student['studentId'],
        "electionId": election_id,
        "candidateIds": ",".join(str(vote['candidate_id']) for vote in votes)
        }

        voteslip_response = requests.post(create_voteslip_url, json=voteslip_data)
        
        if voteslip_response.status_code == 201:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Failed to create voteslip'})

    except json.JSONDecodeError:
        logger.error("Invalid JSON data")
        return JsonResponse({'success': False, 'error': 'Invalid JSON data in request'})

    except Exception as e:
        logger.error(f"Error submitting votes: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

from PIL import Image, ImageDraw, ImageFont

def create_profile_image(initials, output_path, size=256, text_color="white"):
 
    bg_color = (164, 28, 48)
    img = Image.new("RGB", (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", int(size / 2))
    except IOError:
        font = ImageFont.load_default()


    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2.5


    draw.text((text_x, text_y), initials, fill=text_color, font=font)

    img.save(f'static/initials/{output_path}')
    print( output_path)


def getStudentLoggedIn(request):
   
    global Logged_id
    get_user_info(request=request)
    student_by_id = f"http://localhost:5196/api/Students/{Logged_id}"
   
    response = requests.get(student_by_id)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()  # Parse JSON data
    print(data)

  
    return data

def update_results(election_id):
    # API endpoints
    candidate_by_election = f"http://localhost:5196/api/Candidates/election/{election_id}"
    election_by_id = f"http://localhost:5196/api/Elections/{election_id}"
    position_by_election = f"http://localhost:5196/api/Positions/election/{election_id}"

    # Fetch candidates
    response = requests.get(candidate_by_election)
    response.raise_for_status()
    candidates = response.json()

    # Fetch election details
    response = requests.get(election_by_id)
    response.raise_for_status()
    election = response.json()

    # Fetch positions
    response = requests.get(position_by_election)
    response.raise_for_status()
    positions = response.json()

    # Process each position and update winners
    for position in positions:
        # Filter candidates for the current position
        position_candidates = [candidate for candidate in candidates if candidate['positionId'] == position['id']]
        max_winners = position['maxSelection']

        # Skip if the number of candidates is less than or equal to max_winners
        if len(position_candidates) <= max_winners:
            continue

        # Sort candidates by vote count
        sorted_candidates = sorted(position_candidates, key=lambda c: c['voteCount'], reverse=True)

        # Determine the vote count of the last possible winner
        last_winner_vote_count = sorted_candidates[max_winners - 1]['voteCount']

        # Mark candidates as winners or not
        for candidate in sorted_candidates:
            candidate['is_winner'] = candidate['voteCount'] >= last_winner_vote_count
        
        

    # Return the processed data
    return {
        'positions': positions,
        'candidates':  sorted(candidates, key=lambda c: c['voteCount'], reverse=True),
        'election': election
    }


def results_page(request, election_id):
    # Get results and other user context
    results_context = update_results(election_id)
    user_info = get_user_info(request)  # Assuming this is a dict with user info

    # Merge context dictionaries
    context = {**results_context, **user_info}

    # Render the template
    return render(request, 'dashboard_templates/dashboard_check_results.html', context)







def get_voteSlip_by_election_student( election_id, student_id):
    voteslip_url = f"http://localhost:5196/api/VoteSlips/student/{student_id}/election/{election_id}"
    try:
      
        response = requests.get(voteslip_url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()  # Parse JSON data
        voteslips = data.get("result", [])
        return voteslips
    except requests.exceptions.RequestException as e:
      
        print(f"Error fetching data from API: {e}")
        
    

