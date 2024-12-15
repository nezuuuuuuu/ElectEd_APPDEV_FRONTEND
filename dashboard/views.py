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
    # if(verif !=1):
    #     return
    # print(Logged_id)
  
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
        # Send a GET request to the API
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
            
            print(open_date)
            print(close_date)
            print(current_time)
            # Compare dates
            election['is_future'] = open_date > current_time
            election['is_close'] = close_date < current_time
            election['is_present'] = open_date <= current_time <= close_date

            print(f'{election["is_close"]} closed')  # Debugging output
            print(election)

            if(election['is_future']):
                is_future_ctr+=1
                

            

        
    except requests.exceptions.RequestException as e:
        # Handle API errors
        print(f"Error fetching data from API: {e}")
        total_users = pending_orders = completed_orders = active_vendors = inactive_vendors = 0


    context = {
        'elections': elections,
        'is_future_ctr': is_future_ctr
    }
    # context.update(user_info)
    return render(request, 'dashboard_templates/dashboard_votes.html', context | get_user_info(request=request))

def votes_candidates(request, election_id):
    
    election = get_object_or_404(Election, id=election_id)
    positions = Position.objects.filter(election=election)
    candidates = Candidate.objects.filter(election=election).select_related('position')

# Get the search query from the request
    search_query = request.GET.get('q', '').strip()
    current_time =now()
    election.is_close = election.close_date < current_time
    
    

    # Filter candidates based on the current election and search query
    if search_query:
        candidates = Candidate.objects.filter(
            

             Q(name__icontains=search_query) | 
            Q( year__icontains=search_query)|
            Q( course__icontains=search_query)| 
            Q( partylist__icontains=search_query),
            election=election
          
            
           
            
        )
    else:
        candidates = Candidate.objects.filter(election=election)

    for position in positions:
        position.has_candidates=False
        for canidate in candidates:
            if canidate.position==position :
                position.has_candidates=True
    


    # Pass the filtered candidates, positions, and election to the template
    isDisabled= ''
    vote_slip=None
    voted_candidates= None
   
    student=getStudentLoggedIn(request=request)
    try:
        vote_slip = VoteSlip.objects.get(student=student, election=election)
        voted_candidate_ids=str(vote_slip.candidates).replace('\'','').replace('\"','').replace('[','').replace(']','').replace(' ','')

        voted_candidate_ids = voted_candidate_ids.split(',') 
        
        # print(f'{voted_candidate_ids} idsssss')
        isDisabled= 'disabled'
            
    except Exception as e:
        vote_slip = ''
        isDisabled= ''  
        voted_candidate_ids=''  
        

    context = {
        'election': election,
        'positions': positions,
        'candidates': candidates,
        'disabled' : isDisabled,
        'voted_ids': voted_candidate_ids
        

    }

    return render(request, 'dashboard_templates/dashboard_votes_candidates.html',  get_user_info(request))


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
    # try:
    #     # Parse the JSON data from the request body
    #     data = json.loads(request.body)

    #     # Extract votes from the data
    #     votes = data.get('votes', [])
    #     ids=[]
    #     i=0
      
    #     election=None

    #     if not votes:
    #         # If no votes are provided, return an error response
    #         return JsonResponse({'success': False, 'error': 'No votes provided'})

    #     for vote in votes:
    #         n=vote.get('candidate_id')
    #         candidate_id_list=vote.get('candidate_id')
    #         position_list=vote.get('position')
    #         n = len(candidate_id_list)  
    #         for i in range(n):
    #             candidate_id =candidate_id_list[i]
    #             position = position_list[i]

    #             # Check if candidate_id and position are present in each vote
    #             if not candidate_id:
    #                 return JsonResponse({'success': False, 'error': 'Candidate ID missing in vote'})
    #             if not position:
    #                 return JsonResponse({'success': False, 'error': 'Position missing in vote'})

    #             # Attempt to fetch the candidate from the database
    #             try:
    #                 candidate = Candidate.objects.get(id=candidate_id)
    #             except Candidate.DoesNotExist:
    #                 return JsonResponse({'success': False, 'error': f'Candidate with ID {candidate_id} not found'})
    #             ids.append(str(candidate_id))
    #             i+=1
    #             if(election==None):
    #                 election=candidate.election
    #             # Increment the vote count for the selected candidate
    #             candidate.vote_count += 1
    #             candidate.save()
       
    #     # print(candidate.election)
    #     student = getStudentLoggedIn(request=request) 
    #     voteslip = VoteSlip(student=student, election=election,candidates=ids)
           
           
             
    #         # voteslip.full_clean()  # Optional: Validate before saving
 
    #     voteslip.save()
    #     votes_candidates(request, candidate.election.id)
            


    #     # Return a success response if all votes were processed successfully
    #     return JsonResponse({'success': True})

    # except json.JSONDecodeError:
    #     logger.error("Invalid JSON data")
    #     return JsonResponse({'success': False, 'error': 'Invalid JSON data in request'})
    
    # except Exception as e:
    #     # Log any unexpected errors
    #     logger.error(f"Error submitting votes: {e}")
    #     return JsonResponse({'success': False, 'error': str(e)})
    print()

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
    # print(Logged_id)
   
    student = Student.objects.get(student_id=Logged_id)  
    return student

def update_results(election):
    # Get all positions for the election
    positions = Position.objects.filter(election=election)

   

    for position in positions:
         
        # Get the candidates for the current position, ordered by vote count (highest to lowest)
        candidates = Candidate.objects.filter(position=position, election=election).order_by('-vote_count')
        max_winners = position.max_selection
        if len(candidates) <= max_winners:
            continue
        # Get the number of winners for this position based on max_selection
       

        # Find the vote count of the last possible winner (the one at the `max_winners` position)
        if len(candidates) > max_winners:
            last_winner_vote_count = candidates[max_winners - 1].vote_count
        else:
            last_winner_vote_count = candidates[-1].vote_count

        # Mark all candidates with the same vote count as the last winner as winners
        winners = []
        for candidate in candidates:
            if candidate.vote_count >= last_winner_vote_count:
                candidate.is_winner = True
                winners.append(candidate)
            else:
                candidate.is_winner = False
            candidate.save()

def results_page(request, election_id):
    # election = get_object_or_404(Election, id=election_id)
    # print('11111')
    # update_results(election)
    # print('11111')

    # positions = Position.objects.filter(election=election)
    # print('11111')

    # candidates = Candidate.objects.filter(election=election).order_by('-vote_count')
    # print('11111')

    # for position in positions:
    #         position.has_candidates=False
    #         for canidate in candidates:
    #             if canidate.position==position :
    #                 position.has_candidates=True
        

    # context = {
    #     'election': election,
    #     'positions': positions, 
    #     'candidates': candidates,
    # }
    return render(request, 'dashboard_templates/dashboard_check_results.html',   get_user_info(request))