import pickle 
import numpy as np
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Prediction
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from django.db.models import Count, Q

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load the trained model
model_path = os.path.join(BASE_DIR, 'myapp', 'utils', 'failure_model.pkl')
with open(model_path, "rb") as file:
    failure_model = pickle.load(file)

model2_path = os.path.join(BASE_DIR, 'myapp', 'utils', 'failure_type_model.pkl')
with open(model2_path, "rb") as file:
    failure_type_model = pickle.load(file)

dataset_file = os.path.join(BASE_DIR, 'myapp', 'utils', 'predictive_maintenance.csv')
with open(dataset_file, "rb") as f:
    dataset = pd.read_csv(f)

@csrf_exempt 
@api_view(["POST"])  
def predictFailure(request):
    try:
        data = request.data 

        # Extract input values
        mach_type = int(data.get("mach_type", 0))
        air_temp = float(data.get("air_temp", 0.0))
        process_temp = float(data.get("process_temp", 0.0))
        speed = int(data.get("speed", 0))
        torque = float(data.get("torque", 0.0))
        wear = int(data.get("wear", 0))

        # Ensure all inputs are received
        if None in [mach_type, air_temp, process_temp, speed, torque, wear]:
            return Response({"error": "All input fields are required."}, status=400)

        # Prepare input for model prediction
        input_data = np.array([[mach_type, air_temp, process_temp, speed, torque, wear]])

        # Predict failure risk (probability)
        failure_risk = failure_model.predict_proba(input_data)[0][1] * 100 # Assuming second column is failure probability

        # Predict failure type
        failure_type_pred = failure_type_model.predict(input_data)  # Returns an array
        failure_type = failure_type_pred[0] if failure_risk > 70 else "No Failure"

        # Save prediction in the database
        prediction = Prediction(
            mach_type=mach_type,
            air_temp=air_temp,
            process_temp=process_temp,
            rot_speed=speed,
            torque=torque,
            tool_wear=wear,
            failure_risk=failure_risk,
            failure_type=failure_type,
        )
        prediction.save()

        # Render response with prediction results
        return Response({"failure_risk": failure_risk, "failure_type": failure_type})

    except (ValueError, KeyError, TypeError) as e:
        return Response({"error": f"Invalid input: {str(e)}"}, status=400)

    except Exception as e:
        return Response({"error": f"Server error: {str(e)}"}, status=500)
    

def chartData(request):
    # Failure vs No Failure
    total_count = Prediction.objects.count()
    failure_count = Prediction.objects.filter(failure_type__isnull=False).exclude(failure_type="No Failure").count()
    no_failure_count = total_count - failure_count
    target_counts = {
        "No Failure": no_failure_count,
        "Failure": failure_count
    }

    # Counts for types of failures (excluding "No Failure")
    failure_qs = Prediction.objects.exclude(failure_type="No Failure")
    failure_type_counts = failure_qs.values('failure_type').annotate(count=Count('failure_type'))

    failure_percentages = {
        item['failure_type']: round((item['count'] / failure_count) * 100, 2)
        for item in failure_type_counts
    }

    # Failure and No Failure counts grouped by machine type
    failure_counts = Prediction.objects.filter(failure_type__isnull=False).exclude(failure_type="No Failure") \
        .values('mach_type').annotate(failure_count=Count('id'))

    no_failure_counts = Prediction.objects.filter(Q(failure_type="No Failure") | Q(failure_type__isnull=True)) \
        .values('mach_type').annotate(no_failure_count=Count('id'))

    # Convert to DataFrames for easier merging
    df_failure = pd.DataFrame(failure_counts)
    df_no_failure = pd.DataFrame(no_failure_counts)

    df_merged = pd.merge(df_failure, df_no_failure, on='mach_type', how='outer').fillna(0)
    df_merged[['failure_count', 'no_failure_count']] = df_merged[['failure_count', 'no_failure_count']].astype(int)

    # Product type vs all the failure types
    failure_type_matrix = failure_qs.values('mach_type', 'failure_type').annotate(count=Count('id'))
    df_matrix = pd.DataFrame(failure_type_matrix)
    result = {}
    if not df_matrix.empty:
        pivot = df_matrix.pivot(index='mach_type', columns='failure_type', values='count').fillna(0).astype(int)
        result = pivot.to_dict(orient='index')

    return JsonResponse({
        "target_counts": target_counts,
        "failure_percentages": failure_percentages,
        "failure_counts": df_merged.to_dict(orient='records'),
        "failure_type_counts": result
    })

