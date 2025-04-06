
<h1>Ride Sharing Platform – Django</h1>

<p>This project is a simple ride-sharing backend system built with <strong>Django</strong> and <strong>Django REST Framework</strong>. It supports functionality for riders to create ride requests, and for drivers to accept and track rides.</p>

<h2>Features</h2>
<ul>
  <li>Ride creation and management</li>
  <li>Driver and rider signup/signin</li>
  <li>Ride status updates</li>
  <li>Driver location updates and ride tracking</li>
  <li>Ride matching logic</li>
  <li>Test coverage for models and endpoints</li>
</ul>

<h2>Setup Instructions</h2>

<h3>Clone the repository</h3>
<pre><code>git clone https://github.com/alfik1/Ride-sharing-django.git
cd Ride-sharing-django
</code></pre>

<h3>Create and activate a virtual environment</h3>
<pre><code>python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
</code></pre>

<h3>Install dependencies</h3>
<pre><code>pip install -r requirements.txt
</code></pre>

<h3>Apply migrations</h3>
<pre><code>python manage.py migrate
</code></pre>

<h3>Run the server</h3>
<pre><code>python manage.py runserver
</code></pre>

<h3>Run tests</h3>
<pre><code>python manage.py test
</code></pre>

<h2>API Endpoints</h2>

<h3>Ride-related</h3>
<ul>
  <li><code>POST /create-ride/</code> – Create a new ride request</li>
  <li><code>GET /ride-details/&lt;int:id&gt;/</code> – Get ride details</li>
  <li><code>GET /my-rides/</code> – List rides for the authenticated user</li>
  <li><code>PATCH /&lt;int:ride_id&gt;/update-status/</code> – Update status of a ride</li>
  <li><code>POST /accept-ride/</code> – Driver accepts a ride</li>
  <li><code>PATCH /&lt;int:ride_id&gt;/update-location/</code> – Update current location of a driver on a ride</li>
  <li><code>POST /&lt;int:ride_id&gt;/match-driver/</code> – Match a driver to a ride</li>
</ul>

<h3>Auth & Profile</h3>
<ul>
  <li><code>POST /profile-signup</code> – Register a new driver or rider profile</li>
  <li><code>POST /signin</code> – User signin</li>
  <li><code>PATCH /update-driver-location/</code> – Update driver’s real-time location</li>
</ul>

</body>
</html>


