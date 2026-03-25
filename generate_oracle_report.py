from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
import math

def draw_header(c, width, height, oracle_blue):
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(oracle_blue)
    c.drawString(0.75*inch, height - 0.5*inch, "[ORACLE TECHNICAL SPECIFICATION // TS-001]")
    c.setStrokeColor(oracle_blue)
    c.setLineWidth(0.5)
    c.line(0.75*inch, height - 0.6*inch, width - 0.75*inch, height - 0.6*inch)

def draw_footer(c, width, height, slate_grey):
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(slate_grey)
    c.drawCentredString(width/2, 0.4*inch, "© 2026 JMc Associates LLC // James McCabe | ModernCYPH3R.com // Confidential Transmission")

def generate_v8_final_manifesto():
    file_path = "ORACLE_DEAD_ZONE_REPORT.pdf"
    c = canvas.Canvas(file_path, pagesize=LETTER)
    width, height = LETTER

    # Brand Colors
    obsidian = HexColor("#020617")
    midnight = HexColor("#0f172a")
    oracle_blue = HexColor("#38bdf8")
    emerald = HexColor("#10b981")
    cloud_white = HexColor("#f8fafc")
    slate_grey = HexColor("#94a3b8")
    crimson = HexColor("#ef4444")
    gold = HexColor("#f59e0b")

    # --- PAGE 1: THE COVER ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    c.setStrokeColor(oracle_blue); c.setLineWidth(0.5); c.setStrokeAlpha(0.08)
    for x in range(0, int(width), 30): c.line(x, 0, x, height)
    for y in range(0, int(height), 30): c.line(0, y, width, y)
    c.setStrokeAlpha(1.0)
    c.setFont("Helvetica-Bold", 55); c.setFillColor(cloud_white)
    c.drawString(1*inch, height - 3*inch, "THE DEAD")
    c.drawString(1*inch, height - 3.8*inch, "ZONE REPORT")
    c.setStrokeColor(oracle_blue); c.setLineWidth(4); c.line(1*inch, height - 4.2*inch, 4.5*inch, height - 4.2*inch)
    c.setFont("Helvetica-Bold", 18); c.setFillColor(oracle_blue)
    c.drawString(1*inch, height - 4.8*inch, "A Technical Abstract on Mathematical")
    c.drawString(1*inch, height - 5.1*inch, "Variance and Structural Deployment")
    c.setFont("Helvetica", 14); c.setFillColor(slate_grey)
    c.drawString(1*inch, height - 6.5*inch, "James McCabe | ModernCYPH3R.com")
    c.drawString(1*inch, height - 6.8*inch, "Date: March 18, 2026")
    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 2: THE RANDOMNESS PARADOX ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 20); c.setFillColor(cloud_white)
    c.drawString(0.75*inch, height - 1.2*inch, "01. THE RANDOMNESS PARADOX")
    c.setFont("Helvetica", 11)
    text1 = [
        "The lottery is a game of pure mathematical variance. Most participants attempt to defeat this with 'luck.'",
        "They use birthdays, anniversaries, or—the most lethal error—the automated Quick Pick.",
        "",
        "The state relies on your lack of discipline. Random Number Generators are mathematically blind. They",
        "populate every possible combination in the matrix, regardless of how statistically invisible it is in a human",
        "lifetime. Randomness ensures a flat distribution where 50% of every dollar is retained without a fight.",
        "",
        "The Oracle is the structural antidote. We do not predict the future; we identify where the future is most",
        "likely to occur. We treat the lottery like a technical deployment, not a game of chance. If you are going",
        "to play, you must involve math to give yourself a fighting chance on solid footing."
    ]
    y = height - 1.6*inch
    for line in text1:
        c.drawString(0.75*inch, y, line); y -= 15
    c.setFillColor(HexColor("#450a0a")); c.rect(0.75*inch, y - 1*inch, 7*inch, 0.6*inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#f87171")); c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, y - 0.7*inch, "INDUSTRIAL REALITY: THE QUICK PICK IS A VOLUNTARY TAX.")
    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 3: CENTER OF MASS ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 20); c.setFillColor(cloud_white)
    c.drawString(0.75*inch, height - 1.2*inch, "02. THE MATHEMATICAL CENTER OF MASS")
    y = height - 1.6*inch
    c.setFont("Helvetica-Bold", 13); c.setFillColor(oracle_blue)
    c.drawString(0.75*inch, y, "PART A: THE STARTING NUMBER SPATIAL ANOMALY")
    chart_y = y - 1.6*inch
    c.setFillColor(oracle_blue); c.rect(2.5*inch, chart_y, 1*inch, 1.2*inch, fill=1)
    c.setFillColor(cloud_white); c.setFont("Helvetica-Bold", 9); c.drawCentredString(3.0*inch, chart_y + 1.3*inch, "17.8%")
    c.drawCentredString(3.0*inch, chart_y - 0.2*inch, "Powerball")
    c.setFillColor(crimson); c.rect(4.5*inch, chart_y, 1*inch, 0.4*inch, fill=1)
    c.setFillColor(cloud_white); c.drawCentredString(5.0*inch, chart_y + 0.5*inch, "7.1%")
    c.drawCentredString(5.0*inch, chart_y - 0.2*inch, "Mega Millions")
    c.saveState(); c.translate(1.0*inch, chart_y + 0.1*inch); c.rotate(90)
    c.setFont("Helvetica-Bold", 8); c.setFillColor(slate_grey); c.drawString(0, 0, "Prob of Start Number > 20"); c.restoreState()
    y = chart_y - 0.8*inch
    c.setFont("Helvetica", 10); c.setFillColor(cloud_white)
    c.drawString(0.75*inch, y, "Mega Millions clustering is absolute. Combinations starting > 20 are 93% statistical traps.")
    c.setFont("Helvetica-Bold", 13); c.setFillColor(oracle_blue); c.drawString(0.75*inch, y - 0.6*inch, "PART B: THE CASH GAME CLASSIFICATION")
    c.setFont("Helvetica", 10.5); c.setFillColor(cloud_white)
    text_cash = [
        "In smaller matrix games like Cash 5 (VA/TX), the gravity is extreme. With only 45 balls, the math",
        "forces a heavy cluster at the low end. 74.4% of draws start between 1 and 10."
    ]
    y_cash = y - 0.9*inch
    for line in text_cash:
        c.drawString(0.75*inch, y_cash, line); y_cash -= 14
    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 4: MATH LESSON & PICK 3 ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 14); c.setFillColor(oracle_blue)
    c.drawString(0.75*inch, height - 1.2*inch, "PART C: COMBINATORIAL SPREAD VS. SUM DISTRIBUTION")
    c.setFont("Helvetica", 10.5); c.setFillColor(cloud_white)
    math_lesson = [
        "Combinatorial Math (Powerball/Lotto) deals with 'Sampling Without Replacement'—the order doesn't",
        "matter, but the spatial spread (gaps between numbers) is everything. We look at 'Triplets' to ensure",
        "coverage. Distribution (Pick 3/4) deals with 'Sampling With Replacement'—order is king. We use",
        "Sum Distribution to find the Mathematical Center of Mass where the numbers are forced to cluster."
    ]
    y = height - 1.5*inch
    for line in math_lesson:
        c.drawString(0.75*inch, y, line); y -= 14
    y_curve = y - 2.5*inch
    c.setStrokeColor(emerald); c.setLineWidth(2.5)
    p = c.beginPath(); p.moveTo(1.5*inch, y_curve)
    p.curveTo(2.5*inch, y_curve, 3.5*inch, y_curve + 1.8*inch, 4*inch, y_curve + 1.8*inch)
    p.curveTo(4.5*inch, y_curve + 1.8*inch, 5.5*inch, y_curve, 6.5*inch, y_curve); c.drawPath(p)
    c.setFillColor(emerald); c.setFont("Helvetica-Bold", 10); c.drawCentredString(4*inch, y_curve + 2.0*inch, "PICK 3 CENTER OF MASS: SUM 13-15")
    c.setFillColor(midnight); c.rect(0.75*inch, y_curve - 1.6*inch, 7*inch, 1.2*inch, fill=1, stroke=1)
    c.setStrokeColor(emerald); c.setFillColor(oracle_blue); c.setFont("Helvetica-Bold", 12)
    c.drawString(1.0*inch, y_curve - 0.7*inch, "THE TECHNICIAN'S CREED:")
    c.setFont("Helvetica", 10.5); c.setFillColor(cloud_white)
    c.drawString(1.0*inch, y_curve - 0.95*inch, "Stop guessing. The Oracle is a heavy-duty industrial sieve designed to filter out the")
    c.drawString(1.0*inch, y_curve - 1.15*inch, "statistical trash. We play the center of gravity where history actually happens.")
    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 5: THE ASSEMBLY LINE ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 20); c.setFillColor(cloud_white)
    c.drawString(0.75*inch, height - 1.1*inch, "03. THE ORACLE ASSEMBLY LINE")
    c.setFont("Helvetica", 11); c.drawString(0.75*inch, height - 1.5*inch, "We do not predict. We architect. The flow from 10-year history to deployment is a technical sequence.")
    start_y = height - 2.8*inch
    # Box Flow: DB -> Prophet -> Pool -> Pragmatist -> Scouter -> Vault
    c.setStrokeColor(oracle_blue); c.setFillColor(midnight); c.rect(0.75*inch, start_y, 1.5*inch, 0.4*inch, fill=1)
    c.setFillColor(cloud_white); c.setFont("Helvetica-Bold", 7); c.drawCentredString(1.5*inch, start_y + 0.15*inch, "10Y HISTORICAL DB")
    c.setStrokeColor(oracle_blue); c.line(2.25*inch, start_y+0.2*inch, 2.75*inch, start_y+0.2*inch)
    c.rect(2.75*inch, start_y, 1.5*inch, 0.4*inch, fill=1)
    c.drawCentredString(3.5*inch, start_y + 0.15*inch, "PROPHET ENGINE")
    c.line(4.25*inch, start_y+0.2*inch, 4.75*inch, start_y+0.2*inch)
    c.setStrokeColor(emerald); c.rect(4.75*inch, start_y, 1.5*inch, 0.4*inch, fill=1)
    c.drawCentredString(5.5*inch, start_y + 0.15*inch, "15-NUMBER SMART POOL")
    c.line(6.25*inch, start_y+0.2*inch, 6.75*inch, start_y+0.2*inch)
    c.setStrokeColor(oracle_blue); c.rect(6.75*inch, start_y, 1*inch, 0.4*inch, fill=1)
    c.drawCentredString(7.25*inch, start_y + 0.15*inch, "DEPLOY")
    
    y = start_y - 0.6*inch
    c.setFont("Helvetica-Bold", 10); c.setFillColor(oracle_blue); c.drawString(0.75*inch, y, "ENGINE LOGIC DEEP-DIVE:")
    eng_text = [
        "• MARKOV CHAINS: Models the 'State Machine' of the draw. If ball 14 hit, what ball follows it historically?",
        "• POISSON TENSION: Calculates overdue scores. When a number deviates from its mean, tension builds.",
        "• BASE FREQUENCY: Adjusts for microscopic physical variance in ball sets over a 10-year sample.",
        "• PATTERN SCOUTER: The final bouncer. It purges consecutive sequences and historical collisions."
    ]
    y -= 0.3*inch
    for line in eng_text:
        c.setFont("Helvetica", 10); c.setFillColor(cloud_white); c.drawString(0.75*inch, y, line); y -= 16
    c.setFillColor(midnight); c.rect(0.75*inch, y - 1.2*inch, 7*inch, 1.0*inch, fill=1, stroke=1)
    c.setStrokeColor(oracle_blue); c.setFillColor(oracle_blue); c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, y - 0.5*inch, "CRITICAL PROTOCOL: NOT A LOTTERY PREDICTOR")
    c.setFont("Helvetica", 10); c.setFillColor(cloud_white)
    c.drawCentredString(width/2, y - 0.8*inch, "The Oracle manages the distribution of your play against statistical noise.")
    c.drawCentredString(width/2, y - 1.05*inch, "It cannot predict future events, only eliminate the 70% of reality that will never occur.")
    draw_footer(c, width, height, slate_grey); c.showPage()

    # --- PAGE 6: THE COMMAND ---
    c.setFillColor(obsidian); c.rect(0, 0, width, height, fill=1)
    draw_header(c, width, height, oracle_blue)
    c.setFont("Helvetica-Bold", 30); c.setFillColor(cloud_white); c.drawCentredString(width/2, height - 2.5*inch, "INITIALIZE THE PROTOCOL")
    c.setFont("Helvetica", 12); c.setFillColor(cloud_white)
    cta_text = [
        "You are now standing at the threshold of the Vault. The data you have read is the map;",
        "the Oracle is the vehicle. Most will continue to play the Quick Pick donation game.",
        "A small syndicate of technicians will choose to play with structural mathematical footing.",
        "The Vault is initialized. The data is current. The choice is yours."
    ]
    y_cta = height - 3.2*inch
    for line in cta_text:
        c.drawCentredString(width/2, y_cta, line); y_cta -= 18
    c.setFillColor(midnight); c.rect(1.25*inch, 2.5*inch, 5.5*inch, 3.2*inch, fill=1, stroke=1)
    c.setStrokeColor(oracle_blue); c.setFont("Helvetica-Bold", 16); c.setFillColor(oracle_blue); c.drawString(1.5*inch, 5.2*inch, "PRO TIER ACTIVATION:")
    c.setFont("Helvetica", 11); c.setFillColor(cloud_white)
    perks = [
        "• 50 Daily High-Volume Generations across all sectors.",
        "• Advanced Markov Transition Scoring & Overdue Tension Dashboards.",
        "• Professional Syndicate PDF Manifest Exporters for multi-user deployment.",
        "• Real-Time API Ingestion for NAT (PB/MM), VA, NY, TX, and CA games.",
        "• (NEW) Weekly state additions ensuring your sector is always covered."
    ]
    yp = 4.8*inch
    for p in perks: c.drawString(1.7*inch, yp, p); yp -= 22
    c.setFillColor(midnight); c.rect(width/2 - 2.5*inch, 2.8*inch, 5*inch, 0.6*inch, fill=1, stroke=1)
    c.setStrokeColor(emerald); c.setFillColor(emerald); c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, 3.05*inch, "DEPOY AT: ORACLEAPP.MODERNCYPH3R.COM")
    draw_footer(c, width, height, slate_grey); c.save()
    print("Industrial Manifesto v8.0 generated: ORACLE_DEAD_ZONE_REPORT.pdf")

if __name__ == "__main__":
    generate_v8_final_manifesto()
