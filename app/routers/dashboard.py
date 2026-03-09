# app/routers/dashboard.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.db_service import db_service
import json
from datetime import datetime

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Interactive HTML dashboard"""
    
    leads = db_service.get_leads()
    
    # Prepare data for charts
    categories = {}
    ratings = []
    locations = {}
    
    for lead in leads:
        cat = lead.category or 'unknown'
        categories[cat] = categories.get(cat, 0) + 1
        
        if lead.rating:
            try:
                ratings.append(float(lead.rating))
            except:
                pass
        
        loc = lead.location or 'Unknown'
        locations[loc] = locations.get(loc, 0) + 1
    
    # Top categories
    top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Top locations
    top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # HTML Dashboard
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clutch Lead Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .stat-number {{ font-size: 36px; font-weight: bold; color: #667eea; }}
            .stat-label {{ color: #666; font-size: 14px; }}
            .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .chart-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background: #667eea; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            .badge {{ background: #764ba2; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Clutch Lead Dashboard</h1>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(leads)}</div>
                <div class="stat-label">Total Companies</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for l in leads if l.email and l.email != 'Not available')}</div>
                <div class="stat-label">Companies with Email</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for l in leads if getattr(l, 'phone', None) and l.phone != 'Not available')}</div>
                <div class="stat-label">Companies with Phone</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for l in leads if getattr(l, 'linkedin', None) and l.linkedin != 'Not available')}</div>
                <div class="stat-label">Companies with LinkedIn</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📈 Top Categories</h3>
                <canvas id="categoryChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>⭐ Rating Distribution</h3>
                <canvas id="ratingChart"></canvas>
            </div>
        </div>
        
        <div style="margin-top: 20px;" class="chart-card">
            <h3>📍 Top Locations</h3>
            <table>
                <tr><th>Location</th><th>Companies</th></tr>
                {"".join(f"<tr><td>{loc}</td><td>{count}</td></tr>" for loc, count in top_locations)}
            </table>
        </div>
        
        <script>
            // Category Chart
            new Chart(document.getElementById('categoryChart'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps([c[0] for c in top_categories])},
                    datasets: [{{
                        label: 'Companies',
                        data: {json.dumps([c[1] for c in top_categories])},
                        backgroundColor: '#667eea'
                    }}]
                }},
                options: {{ responsive: true }}
            }});
            
            // Rating Chart
            new Chart(document.getElementById('ratingChart'), {{
                type: 'doughnut',
                data: {{
                    labels: ['5 Star (4.8+)', '4.5 Star (4.5-4.8)', '4 Star (4.0-4.5)', 'Below 4'],
                    datasets: [{{
                        data: [
                            {sum(1 for r in ratings if r >= 4.8)},
                            {sum(1 for r in ratings if 4.5 <= r < 4.8)},
                            {sum(1 for r in ratings if 4.0 <= r < 4.5)},
                            {sum(1 for r in ratings if r < 4.0)}
                        ],
                        backgroundColor: ['#4CAF50', '#8BC34A', '#FFC107', '#F44336']
                    }}]
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)