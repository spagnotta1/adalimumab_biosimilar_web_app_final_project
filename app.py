from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import sqlite3


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database and pickle file paths
DB_PATH = "E:/Masters of Data Science Program - All Materials/Semester 2 Classes_1_13_2025/Applied Database Technologies/Final Project/clinical_trials.db"
PICKLE_PATH = "E:\Masters of Data Science Program - All Materials\Semester 2 Classes_1_13_2025\Applied Database Technologies\Final Project\clinical_trials.pkl"

# Function to update the pickle file
def update_pickle():
    # Read the database into a DataFrame
    conn = sqlite3.connect(DB_PATH)
    query = """
           SELECT DISTINCT(a.ndc_code) as ndc,
           a.drug_name,
           a.active_ingredients,
           a.strength,
           b.labeler_name,
           a.action_type as status,
           a.action_date as ct_end_date,
           b.marketing_start_date as gtm_date
    FROM fda_approved a, drug_data b
    WHERE a.ndc_code = b.product_ndc
    AND a.drug_name != 'HUMIRA'
    AND a.ndc_code != '65219-556';
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Perform calculations for the GTM in years and days
      # Perform calculations
    df['ct_end_date'] = pd.to_datetime(df['ct_end_date'], format='%m/%d/%Y', errors='coerce')
    df['gtm_date'] = pd.to_datetime(df['gtm_date'], format='%m/%d/%Y', errors='coerce')
    df['days_to_brand_launch'] = df['gtm_date'] - df['ct_end_date']
    #df['Years to Brand Launch'] = df['days_to_brand_launch'].dt.days / 365.25
    df.rename(columns={
        'ndc': 'NDC',
        'drug_name': 'Brand Name',
        'active_ingredients': 'Molecular Name',
        'strength': 'Strength',
        'labeler_name': 'Manufacturer',
        'status': 'Status',
        'ct_end_date': 'Clinical Trial End Date',
        'gtm_date': 'Brand Launch Date',
        'days_to_brand_launch': 'Days to Brand Launch'
    }, inplace=True)
    df.to_pickle(PICKLE_PATH)

# Load DataFrame from pickle file
df = pd.read_pickle(PICKLE_PATH)


@app.route('/')
def dashboard():
    table_html = df.to_html(classes='table table-striped', index=False)
    return render_template('dashboard.html',
                          title='Adalimumab (Biosimilar) Clinical Trials',
                          table_html=table_html,
                          trials=df.to_dict('records'))  


# Create: Add a new trial
@app.route('/create', methods=['GET', 'POST'])
def create_trial():
    if request.method == 'POST':
        try:
            ndc_code = request.form['ndc_code']
            drug_name = request.form['drug_name']
            active_ingredients = request.form['active_ingredients']
            strength = request.form['strength']
            dosage = request.form['dosage']
            route = request.form['route']
            mrkt_status = request.form['mrkt_status']
            te_code = request.form['te_code']
            rld = request.form['rld']
            rs = request.form['rs']
            submission = request.form['submission']
            labeler_name = request.form['labeler_name']
            action_type = request.form['action_type']
            action_date = request.form['action_date']
            marketing_start_date = request.form['marketing_start_date']

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fda_approved (ndc_code, drug_name, active_ingredients, strength, dosage, route, mrkt_status, te_code, rld, rs, submission, action_type, action_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ndc_code, drug_name, active_ingredients, strength, dosage, route, mrkt_status, te_code, rld, rs, submission, action_type, action_date))
            cursor.execute("""
                INSERT INTO drug_data (product_ndc, labeler_name, marketing_start_date)
                VALUES (?, ?, ?)
            """, (ndc_code, labeler_name, marketing_start_date))
            conn.commit()
            conn.close()
            update_pickle()  #Update the pickle file
            flash('Clinical Trial record created successfully!')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f'Error creating Clinical Trial: {str(e)}', 'ERROR')
    return render_template('create_trial.html')


# Update: Edit an existing clinical trial record
@app.route('/update/<ndc_code>', methods=['GET', 'POST'])
def update_trial(ndc_code):
    if request.method == 'POST':
        try:
            drug_name = request.form['drug_name']
            active_ingredients = request.form['active_ingredients']
            strength = request.form['strength']
            labeler_name = request.form['labeler_name']
            action_type = request.form['action_type']
            action_date = request.form['action_date']
            marketing_start_date = request.form['marketing_start_date']

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fda_approved
                SET drug_name = ?, active_ingredients = ?, strength = ?, action_type = ?, action_date = ?
                WHERE ndc_code = ?
            """, (drug_name, active_ingredients, strength, action_type, action_date, ndc_code))
            cursor.execute("""
                UPDATE drug_data
                SET labeler_name = ?, marketing_start_date = ?
                WHERE product_ndc = ?
            """, (labeler_name, marketing_start_date, ndc_code))
            conn.commit()
            conn.close()
            update_pickle()  # Update the pickle file
            flash('Clinical Trial record updated successfully!')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f'Error updating Clinical Trial: {str(e)}', 'ERROR')
    else:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.ndc_code, a.drug_name, a.active_ingredients, a.strength, b.labeler_name,
                   a.action_type, a.action_date, b.marketing_start_date
            FROM fda_approved a, drug_data b
            WHERE a.ndc_code = b.product_ndc AND a.ndc_code = ?
        """, (ndc_code,))
        trial = cursor.fetchone()
        conn.close()
        if trial:
            trial_data = {
                'ndc_code': trial[0], 'drug_name': trial[1], 'active_ingredients': trial[2],
                'strength': trial[3], 'labeler_name': trial[4], 'action_type': trial[5],
                'action_date': trial[6], 'marketing_start_date': trial[7]
            }
            return render_template('update_trial.html', trial=trial_data)
        flash('Trial not found!', 'danger')
        return redirect(url_for('dashboard'))
    

# Delete: Delete a clinical trial record
@app.route('/delete/<ndc_code>', methods=['POST'])
def delete_trial(ndc_code):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fda_approved WHERE ndc_code = ?", (ndc_code,))
        cursor.execute("DELETE FROM drug_data WHERE product_ndc = ?", (ndc_code,))
        conn.commit()
        conn.close()
        update_pickle()  # Update the pickle file
        flash('Clinical Trial record deleted successfully!')
    except sqlite3.Error as e:
        flash(f'Error deleting Clinical Trial: {str(e)}', 'ERROR')
    return redirect(url_for('dashboard'))


# Run the application
if __name__ == '__main__':
    app.run(debug=True)