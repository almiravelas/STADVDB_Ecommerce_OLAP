import os
import pandas as pd
# Assuming standardize_gender and parse_date_formats are in '.utils'
# from .utils import standardize_gender, parse_date_formats
# Placeholder functions if utils.py is not available in this context
def standardize_gender(gender_series):
    gender_map = {'male': 'Male', 'female': 'Female', 'm': 'Male', 'f': 'Female'}
    return gender_series.str.lower().map(gender_map).fillna('Other')
def parse_date_formats(date_str):
    # Add robust date parsing logic if needed
    return pd.to_datetime(date_str, errors='coerce')


def transform_dim_user(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw user data into a user dimension table with continent mapping."""
    if df is None:
        return None

    print("Transforming user data...")
    df = df.copy()

    # --- Rename id to user_key ---
    if 'id' in df.columns:
        df.rename(columns={'id': 'user_key'}, inplace=True)
    if 'user_key' not in df.columns:
        # Create a default user_key if 'id' or 'user_key' is missing
        df['user_key'] = df.index + 1 # Simple sequential key

    # --- Fill missing required fields ---
    for col in ['username', 'city', 'country']:
        if col not in df.columns:
            df[col] = 'Unknown'
        # Ensure even existing columns handle potential None/NaN values before string ops
        df[col] = df[col].fillna('Unknown')


    # --- Standardize gender ---
    if 'gender' in df.columns:
         # Fill NaNs before converting to string to avoid errors
        df['gender'] = standardize_gender(df['gender'].fillna('Other').astype(str))
    else:
        df['gender'] = 'Other'


    # --- Full name ---
    # Use .get() with default Series of empty strings, handle potential NaNs
    first = df.get('firstName', pd.Series([''] * len(df))).fillna('')
    last = df.get('lastName', pd.Series([''] * len(df))).fillna('')
    # Ensure correct string concatenation and handle empty results
    df['full_name'] = (first.astype(str) + ' ' + last.astype(str)).str.strip()
    df['full_name'] = df['full_name'].replace('', 'Unknown')


    # --- Normalize capitalization ---
    for col in ['city', 'country']:
        # Chain operations: fillna, replace empty string, convert type, then apply string method
        df[col] = df[col].fillna('Unknown').replace('', 'Unknown').astype(str).str.title()


    # --- Load mapping from users.csv ---
    # This logic expects users.csv to have country -> continent/region mapping.
    # The provided users.csv does NOT have this format.
    # It will likely fall back to the dictionary mapping below.
    csv_path = os.path.join(os.path.dirname(__file__), "users.csv")

    mapping_successful = False # Flag to track if custom mapping worked
    if os.path.exists(csv_path):
        try:
            mapping_df = pd.read_csv(csv_path)
            # Standardize column names from CSV
            mapping_df.columns = mapping_df.columns.str.lower().str.strip()

            # --- Determine country and continent columns ---
            country_col_options = ["country", "country_name"]
            continent_col_options = ["continent", "region"]

            country_col = next((c for c in country_col_options if c in mapping_df.columns), None)
            continent_col = next((c for c in continent_col_options if c in mapping_df.columns), None)

            if country_col and continent_col:
                # Prepare mapping data: standardize case and drop duplicates
                mapping_df[country_col] = mapping_df[country_col].astype(str).str.title()
                mapping_df[continent_col] = mapping_df[continent_col].astype(str).str.title()
                continent_map_data = mapping_df[[country_col, continent_col]].drop_duplicates(subset=[country_col])

                # Merge with the main DataFrame
                df = df.merge(
                    continent_map_data,
                    how="left",
                    left_on="country", # Assumes 'country' column exists in df after normalization
                    right_on=country_col
                )

                # Assign continent and clean up
                df["continent"] = df[continent_col].fillna("Other")
                df.drop(columns=[country_col, continent_col], errors="ignore", inplace=True)

                print(f"✅ Loaded custom country-to-continent mapping from {csv_path}")
                mapping_successful = True # Set flag if successful
            else:
                 print(f"⚠️ users.csv found at {csv_path}, but required columns (country/continent or region) are missing.")

        except Exception as e:
            print(f"⚠️ Failed to load or process custom mapping file '{csv_path}': {e}")
            # Fallback handled below by checking the flag

    else:
        print(f"⚠️ Custom mapping file users.csv not found at {csv_path}.")

    # --- Fallback to Dictionary Mapping ---
    if not mapping_successful:
        print("🔧 Using built-in comprehensive country-to-continent mapping.")
        # --- Comprehensive Country to Continent Mapping (Expanded Fallback) ---
        country_to_continent = {
            # Asia
            'Afghanistan': 'Asia', 'Armenia': 'Asia', 'Azerbaijan': 'Asia', 'Bahrain': 'Asia',
            'Bangladesh': 'Asia', 'Bhutan': 'Asia', 'Brunei Darussalam': 'Asia', 'Cambodia': 'Asia',
            'China': 'Asia', 'Cyprus': 'Asia', 'Georgia': 'Asia', # Transcontinental (often Europe)
            'Hong Kong': 'Asia', 'India': 'Asia', 'Indonesia': 'Asia', 'Iran': 'Asia',
            'Iraq': 'Asia', 'Israel': 'Asia', 'Japan': 'Asia', 'Jordan': 'Asia',
            'Kazakhstan': 'Asia', 'Kuwait': 'Asia', 'Kyrgyz Republic': 'Asia',
            'Lao People\'s Democratic Republic': 'Asia', 'Lebanon': 'Asia', 'Macao': 'Asia',
            'Malaysia': 'Asia', 'Maldives': 'Asia', 'Mongolia': 'Asia', 'Myanmar': 'Asia',
            'Nepal': 'Asia', 'Democratic People\'s Republic of Korea': 'Asia', 'Oman': 'Asia',
            'Pakistan': 'Asia', 'Palestine': 'Asia', 'Philippines': 'Asia', 'Qatar': 'Asia',
            'Republic of Korea': 'Asia', 'Russian Federation': 'Asia', # Transcontinental (mostly Europe)
            'Saudi Arabia': 'Asia', 'Singapore': 'Asia', 'Sri Lanka': 'Asia',
            'Syrian Arab Republic': 'Asia', 'Taiwan': 'Asia', 'Tajikistan': 'Asia',
            'Thailand': 'Asia', 'Timor-Leste': 'Asia', 'Turkey': 'Asia', # Transcontinental (mostly Asia)
            'Turkmenistan': 'Asia', 'United Arab Emirates': 'Asia', 'Uzbekistan': 'Asia',
            'Vietnam': 'Asia', 'Yemen': 'Asia',

            # Europe
            'Aland Islands': 'Europe', 'Albania': 'Europe', 'Andorra': 'Europe', 'Austria': 'Europe',
            'Belarus': 'Europe', 'Belgium': 'Europe', 'Bosnia and Herzegovina': 'Europe',
            'Bulgaria': 'Europe', 'Croatia': 'Europe', 'Czechia': 'Europe', 'Denmark': 'Europe',
            'Estonia': 'Europe', 'Faroe Islands': 'Europe', 'Finland': 'Europe', 'France': 'Europe',
            'Germany': 'Europe', 'Gibraltar': 'Europe', 'Greece': 'Europe', 'Guernsey': 'Europe',
            'Holy See (Vatican City State)': 'Europe', 'Hungary': 'Europe', 'Iceland': 'Europe',
            'Ireland': 'Europe', 'Isle of Man': 'Europe', 'Italy': 'Europe', 'Jersey': 'Europe',
            'Latvia': 'Europe', 'Liechtenstein': 'Europe', 'Lithuania': 'Europe', 'Luxembourg': 'Europe',
            'Malta': 'Europe', 'Moldova': 'Europe', 'Monaco': 'Europe', 'Montenegro': 'Europe',
            'Netherlands': 'Europe', 'North Macedonia': 'Europe', 'Norway': 'Europe',
            'Poland': 'Europe', 'Portugal': 'Europe', 'Romania': 'Europe',
            'San Marino': 'Europe', 'Serbia': 'Europe', 'Slovakia': 'Europe', 'Slovenia': 'Europe',
            'Spain': 'Europe', 'Svalbard & Jan Mayen Islands': 'Europe', 'Sweden': 'Europe',
            'Switzerland': 'Europe', 'Ukraine': 'Europe', 'United Kingdom': 'Europe',

            # North America
            'Anguilla': 'North America', 'Antigua and Barbuda': 'North America', 'Aruba': 'North America',
            'Bahamas': 'North America', 'Barbados': 'North America', 'Belize': 'North America',
            'Bermuda': 'North America', 'Bonaire, Sint Eustatius and Saba': 'North America', # Netherlands, geographically N. America
            'Canada': 'North America', 'Cayman Islands': 'North America', 'Costa Rica': 'North America',
            'Cuba': 'North America', 'Curacao': 'North America', 'Dominica': 'North America',
            'Dominican Republic': 'North America', 'El Salvador': 'North America', 'Greenland': 'North America',
            'Grenada': 'North America', 'Guadeloupe': 'North America', 'Guatemala': 'North America',
            'Haiti': 'North America', 'Honduras': 'North America', 'Jamaica': 'North America',
            'Martinique': 'North America', 'Mexico': 'North America', 'Montserrat': 'North America',
            'Nicaragua': 'North America', 'Panama': 'North America', # Can be C/S America
            'Puerto Rico': 'North America', 'Saint Barthelemy': 'North America', 'Saint Kitts and Nevis': 'North America',
            'Saint Lucia': 'North America', 'Saint Martin': 'North America', # France, geographically N. America
            'Saint Pierre and Miquelon': 'North America', 'Saint Vincent and the Grenadines': 'North America',
            'Sint Maarten': 'North America', # Netherlands, geographically N. America
            'Trinidad and Tobago': 'North America', # Sometimes S. America
            'Turks and Caicos Islands': 'North America', 'United States': 'North America', # Common name
            'United States of America': 'North America', # Formal name
            'Virgin Islands, U.S.': 'North America', 'Virgin Islands, British': 'North America',

            # South America
            'Argentina': 'South America', 'Bolivia': 'South America', 'Brazil': 'South America',
            'Chile': 'South America', 'Colombia': 'South America', 'Ecuador': 'South America',
            'Falkland Islands (Malvinas)': 'South America', 'French Guiana': 'South America',
            'Guyana': 'South America', 'Paraguay': 'South America', 'Peru': 'South America',
            'Suriname': 'South America', 'Uruguay': 'South America', 'Venezuela': 'South America',

            # Africa
            'Algeria': 'Africa', 'Angola': 'Africa', 'Benin': 'Africa', 'Botswana': 'Africa',
            'Burkina Faso': 'Africa', 'Burundi': 'Africa', 'Cameroon': 'Africa', 'Cape Verde': 'Africa',
            'Central African Republic': 'Africa', 'Chad': 'Africa', 'Comoros': 'Africa',
            'Congo': 'Africa', 'Democratic Republic of the Congo': 'Africa',
            'Cote d\'Ivoire': 'Africa', 'Djibouti': 'Africa', 'Egypt': 'Africa', # Transcontinental (mostly Africa)
            'Equatorial Guinea': 'Africa', 'Eritrea': 'Africa', 'Eswatini': 'Africa', 'Ethiopia': 'Africa',
            'Gabon': 'Africa', 'Gambia': 'Africa', 'Ghana': 'Africa', 'Guinea': 'Africa',
            'Guinea-Bissau': 'Africa', 'Kenya': 'Africa', 'Lesotho': 'Africa', 'Liberia': 'Africa',
            'Libyan Arab Jamahiriya': 'Africa', 'Madagascar': 'Africa', 'Malawi': 'Africa', 'Mali': 'Africa',
            'Mauritania': 'Africa', 'Mauritius': 'Africa', 'Mayotte': 'Africa', 'Morocco': 'Africa',
            'Mozambique': 'Africa', 'Namibia': 'Africa', 'Niger': 'Africa', 'Nigeria': 'Africa',
            'Reunion': 'Africa', 'Rwanda': 'Africa', 'Saint Helena': 'Africa',
            'Sao Tome and Principe': 'Africa', 'Senegal': 'Africa', 'Seychelles': 'Africa',
            'Sierra Leone': 'Africa', 'Somalia': 'Africa', 'South Africa': 'Africa', 'South Sudan': 'Africa',
            'Sudan': 'Africa', 'Tanzania': 'Africa', 'Togo': 'Africa', 'Tunisia': 'Africa',
            'Uganda': 'Africa', 'Western Sahara': 'Africa', 'Zambia': 'Africa', 'Zimbabwe': 'Africa',

            # Oceania (Australia)
            'American Samoa': 'Oceania', 'Australia': 'Oceania', 'Christmas Island': 'Oceania',
            'Cocos (Keeling) Islands': 'Oceania', 'Cook Islands': 'Oceania', 'Fiji': 'Oceania',
            'French Polynesia': 'Oceania', 'Guam': 'Oceania', 'Kiribati': 'Oceania',
            'Marshall Islands': 'Oceania', 'Micronesia': 'Oceania', 'Nauru': 'Oceania',
            'New Caledonia': 'Oceania', 'New Zealand': 'Oceania', 'Niue': 'Oceania',
            'Norfolk Island': 'Oceania', 'Northern Mariana Islands': 'Oceania', 'Palau': 'Oceania',
            'Papua New Guinea': 'Oceania', 'Pitcairn Islands': 'Oceania', 'Samoa': 'Oceania',
            'Solomon Islands': 'Oceania', 'Tokelau': 'Oceania', 'Tonga': 'Oceania', 'Tuvalu': 'Oceania',
            'United States Minor Outlying Islands': 'Oceania', 'Vanuatu': 'Oceania',
            'Wallis and Futuna': 'Oceania',

            # Antarctica
            'Antarctica': 'Antarctica', 'Bouvet Island': 'Antarctica',
            'French Southern Territories': 'Antarctica',
            'Heard Island and McDonald Islands': 'Antarctica',
            'South Georgia and the South Sandwich Islands': 'Antarctica',
            # Add specific known unknowns if needed, otherwise rely on fillna
            'Unknown': 'Other'
        }
        # Apply the mapping, fill any remaining unmapped countries with 'Other'
        # Ensure the 'country' column exists and handles potential previous merge issues
        if 'country' in df.columns:
            df["continent"] = df["country"].map(country_to_continent).fillna("Other")
        else:
            df["continent"] = "Other" # Absolute fallback if country column is missing


    # --- Handle signup_date ---
    # Rename if necessary and handle potential missing column gracefully
    if "createdAt" in df.columns and "signup_date" not in df.columns:
        df.rename(columns={"createdAt": "signup_date"}, inplace=True)

    # Ensure signup_date column exists before processing
    if "signup_date" in df.columns:
        # Use apply with a lambda function for robust parsing
        df["signup_date"] = df["signup_date"].apply(
            lambda x: parse_date_formats(x) if pd.notna(x) else pd.NaT
        )
         # Convert to datetime objects, coercing errors
        df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
    else:
        # If signup_date column doesn't exist at all, create it with NaT
        df["signup_date"] = pd.NaT


    # --- Deduplicate ---
    # Ensure signup_date exists for sorting, handle NaT values if necessary
    sort_columns = ["user_key"]
    if "signup_date" in df.columns:
        sort_columns.append("signup_date")
        # Temporarily fill NaT to allow sorting if mixed types cause issues, then dropna subset
        df.sort_values(by=sort_columns, inplace=True, na_position='first') # Keep NaTs early
    else:
         df.sort_values(by=sort_columns, inplace=True)

    df.drop_duplicates(subset="user_key", keep="last", inplace=True)


    # --- Final dimension output ---
    # Define required columns for the final dimension table
    final_columns = ["user_key", "username", "full_name", "gender", "city", "country", "continent", "signup_date"]
    # Ensure all required columns exist, adding missing ones with default values if necessary
    for col in final_columns:
        if col not in df.columns:
             # Assign appropriate defaults based on expected type
            if col == 'signup_date':
                df[col] = pd.NaT
            elif col == 'user_key': # Should exist by now, but as a safeguard
                 df[col] = -1 # Or another indicator of missing key
            else:
                 df[col] = 'Unknown' # Default for string columns


    dim_df = df[final_columns]

    print("✅ User dimension transformed.")
    return dim_df.reset_index(drop=True)