"""
Profile routes for Nutricount application.
Handles user profile management, GKI calculations, and macro recommendations.
"""

from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

from routes.helpers import get_db, safe_get_json
from src.constants import ERROR_MESSAGES, HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_NOT_FOUND, HTTP_OK
from src.nutrition_calculator import (
    calculate_bmr_katch_mcardle,
    calculate_bmr_mifflin_st_jeor,
    calculate_gki,
    calculate_keto_macros_advanced,
    calculate_lean_body_mass,
    calculate_target_calories,
    calculate_tdee,
)
from src.utils import json_response, safe_float

# Create blueprint
profile_bp = Blueprint("profile", __name__, url_prefix="/api")


@profile_bp.route("/gki", methods=["POST"])
def gki_api():
    """Calculate Glucose-Ketone Index (GKI)"""
    try:
        data = safe_get_json()
        if data is None:
            return (
                jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                HTTP_BAD_REQUEST,
            )

        # Validate input data
        glucose_mgdl = safe_float(data.get("glucose_mgdl"))
        ketones_mgdl = safe_float(data.get("ketones_mgdl"))

        if not glucose_mgdl or not ketones_mgdl:
            return (
                jsonify(
                    json_response(
                        None,
                        "Validation failed",
                        status=HTTP_BAD_REQUEST,
                        errors=["Both glucose_mgdl and ketones_mgdl are required"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        if glucose_mgdl <= 0 or ketones_mgdl <= 0:
            return (
                jsonify(
                    json_response(
                        None,
                        "Validation failed",
                        status=HTTP_BAD_REQUEST,
                        errors=["Glucose and ketones values must be positive"],
                    )
                ),
                HTTP_BAD_REQUEST,
            )

        # Calculate GKI
        gki_result = calculate_gki(glucose_mgdl, ketones_mgdl)

        return jsonify(json_response(gki_result, "GKI calculated successfully"))

    except Exception as e:
        current_app.logger.error(f"GKI API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500


@profile_bp.route("/profile", methods=["GET", "POST", "PUT"])
def profile_api():
    """Get or update user profile"""
    db = None
    try:
        db = get_db()

        if request.method == "GET":
            # Get current profile
            profile = db.execute(
                "SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()

            if profile:
                profile_dict = dict(profile)
                # Calculate age from birth_date

                birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
                today = date.today()
                age = (
                    today.year
                    - birth_date.year
                    - ((today.month, today.day) < (birth_date.month, birth_date.day))
                )
                profile_dict["age"] = age

                return jsonify(json_response(profile_dict, "Profile retrieved successfully"))
            else:
                return (
                    jsonify(json_response(None, "No profile found", status=HTTP_NOT_FOUND)),
                    HTTP_NOT_FOUND,
                )

        else:  # POST or PUT
            data = safe_get_json()
            if data is None:
                return (
                    jsonify(json_response(None, "Invalid JSON", status=HTTP_BAD_REQUEST)),
                    HTTP_BAD_REQUEST,
                )

            # Validate profile data
            errors = []

            # Required fields
            gender = data.get("gender")
            if not gender or gender not in ["male", "female"]:
                errors.append("Gender must be 'male' or 'female'")

            birth_date = data.get("birth_date")
            if not birth_date:
                errors.append("Birth date is required")
            else:
                try:

                    datetime.strptime(birth_date, "%Y-%m-%d")
                except ValueError:
                    errors.append("Birth date must be in YYYY-MM-DD format")

            height_cm = data.get("height_cm")
            if (
                not height_cm
                or not isinstance(height_cm, (int, float))
                or height_cm < 100
                or height_cm > 250
            ):
                errors.append("Height must be between 100 and 250 cm")

            weight_kg = data.get("weight_kg")
            if (
                not weight_kg
                or not isinstance(weight_kg, (int, float))
                or weight_kg < 30
                or weight_kg > 500
            ):
                errors.append("Weight must be between 30 and 500 kg")

            activity_level = data.get("activity_level")
            if not activity_level or activity_level not in [
                "sedentary",
                "light",
                "moderate",
                "active",
                "very_active",
            ]:
                errors.append(
                    "Activity level must be one of: sedentary, light, moderate, active, very_active"
                )

            goal = data.get("goal")
            if not goal or goal not in ["weight_loss", "maintenance", "muscle_gain"]:
                errors.append("Goal must be one of: weight_loss, maintenance, muscle_gain")

            if errors:
                return (
                    jsonify(
                        json_response(
                            None, "Validation failed", status=HTTP_BAD_REQUEST, errors=errors
                        )
                    ),
                    HTTP_BAD_REQUEST,
                )

            # Check if profile exists
            existing_profile = db.execute(
                "SELECT id FROM user_profile ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()

            if existing_profile and request.method == "PUT":
                # Update existing profile
                db.execute(
                    """
                    UPDATE user_profile
                    SET gender = ?, birth_date = ?, height_cm = ?, weight_kg = ?,
                        activity_level = ?, goal = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (
                        gender,
                        birth_date,
                        int(height_cm),
                        float(weight_kg),
                        activity_level,
                        goal,
                        existing_profile[0],
                    ),
                )
                profile_id = existing_profile[0]
            else:
                # Create new profile
                cursor = db.execute(
                    """
                    INSERT INTO user_profile (gender, birth_date, height_cm, weight_kg, activity_level, goal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (gender, birth_date, int(height_cm), float(weight_kg), activity_level, goal),
                )
                profile_id = cursor.lastrowid

            db.commit()

            # Get updated profile
            updated_profile = db.execute(
                "SELECT * FROM user_profile WHERE id = ?", (profile_id,)
            ).fetchone()

            profile_dict = dict(updated_profile)
            # Calculate age

            birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
            today = date.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )
            profile_dict["age"] = age

            return jsonify(
                json_response(
                    profile_dict,
                    (
                        "Profile updated successfully"
                        if existing_profile
                        else "Profile created successfully"
                    ),
                    status=HTTP_CREATED if not existing_profile else HTTP_OK,
                )
            ), (HTTP_CREATED if not existing_profile else HTTP_OK)

    except Exception as e:
        current_app.logger.error(f"Profile API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        if db:
            db.close()


@profile_bp.route("/profile/macros", methods=["GET"])
def profile_macros_api():
    """Calculate daily macros based on user profile"""
    db = None
    try:
        db = get_db()

        # Get current profile
        profile = db.execute(
            "SELECT * FROM user_profile ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()

        if not profile:
            return (
                jsonify(
                    json_response(
                        None,
                        "No profile found. Please create a profile first.",
                        status=HTTP_NOT_FOUND,
                    )
                ),
                HTTP_NOT_FOUND,
            )

        profile_dict = dict(profile)

        # Calculate age

        birth_date = datetime.strptime(profile_dict["birth_date"], "%Y-%m-%d").date()
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        # Calculate BMR using advanced algorithm
        # Use Katch-McArdle if LBM is available (more accurate for high body fat)
        lbm = profile_dict.get("lean_body_mass_kg")
        if lbm is None and profile_dict.get("body_fat_percentage") is not None:
            lbm = calculate_lean_body_mass(
                profile_dict["weight_kg"], profile_dict["body_fat_percentage"]
            )

        if lbm is not None:
            bmr = calculate_bmr_katch_mcardle(lbm)
        else:
            bmr = calculate_bmr_mifflin_st_jeor(
                profile_dict["weight_kg"], profile_dict["height_cm"], age, profile_dict["gender"]
            )

        # Calculate TDEE using advanced algorithm
        tdee = calculate_tdee(bmr, profile_dict["activity_level"])

        # Calculate target calories using advanced algorithm
        target_calories = calculate_target_calories(tdee, profile_dict["goal"])

        # Calculate keto macros using advanced algorithm
        # LBM already calculated above for BMR
        keto_type = profile_dict.get("keto_type", "standard")
        macros = calculate_keto_macros_advanced(
            target_calories, lbm, profile_dict["activity_level"], keto_type, profile_dict["goal"]
        )

        carbs_grams = macros["carbs"]
        protein_grams = macros["protein"]
        fats_grams = macros["fats"]
        carbs_calories = carbs_grams * 4
        protein_calories = protein_grams * 4
        fats_calories = fats_grams * 9

        macros = {
            "bmr": round(bmr, 0),
            "tdee": round(tdee, 0),
            "target_calories": round(target_calories, 0),
            "carbs": round(carbs_grams, 1),
            "protein": round(protein_grams, 1),
            "fats": round(fats_grams, 1),
            "carbs_percentage": round((carbs_calories / target_calories) * 100, 1),
            "protein_percentage": round((protein_calories / target_calories) * 100, 1),
            "fats_percentage": round((fats_calories / target_calories) * 100, 1),
        }

        return jsonify(json_response(macros, "Macros calculated successfully"))

    except Exception as e:
        current_app.logger.error(f"Profile macros API error: {e}")
        return jsonify(json_response(None, ERROR_MESSAGES["server_error"], 500)), 500
    finally:
        if db:
            db.close()
