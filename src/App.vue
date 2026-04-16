<template>
  <!-- main app wrapper -->
  <div class="app">

    <!-- page header with title and subtitle -->
    <header>
      <h1>Wanted Poster Generator</h1>
      <p>Create a DnD wanted poster for your campaign</p>
    </header>

    <main>
      <!-- input form for character details -->
      <div class="form-card">

        <div class="form-group">
          <label>Character Name</label>
          <input v-model="form.name" type="text" placeholder="e.g. Grimshaw the Unyielding" />
        </div>

        <div class="form-group">
          <label>Race</label>
          <input v-model="form.race" type="text" placeholder="e.g. Half-Orc" />
        </div>

        <div class="form-group">
          <label>Class</label>
          <input v-model="form.charClass" type="text" placeholder="e.g. Rogue" />
        </div>

        <div class="form-group">
          <label>Physical Description</label>
          <textarea v-model="form.description" rows="3" placeholder="e.g. Tall, scarred face, missing left eye, wears a black cloak" />
        </div>

        <div class="form-group">
          <label>Crimes Committed</label>
          <textarea v-model="form.crimes" rows="3" placeholder="e.g. Theft of the Crown Jewels, arson, impersonating a noble" />
        </div>

        <div class="form-group">
          <label>Last Known Location</label>
          <input v-model="form.location" type="text" placeholder="e.g. The Underdark, Waterdeep" />
        </div>

        <!-- optional photo upload for the mugshot on the poster -->
        <div class="form-group">
          <label>Character Photo (Optional)</label>
          <input
            type="file"
            accept="image/*"
            @change="handlePhotoUpload"
            class="file-input"
          />
          <p class="optional-note">Upload a photo to use as your mugshot on the poster</p>
          <!-- preview the uploaded photo before generating -->
          <img v-if="uploadedPhoto" :src="uploadedPhoto" class="photo-preview" />
        </div>

        <!-- button disables while waiting for the API response -->
        <button @click="generatePoster" :disabled="loading">
          {{ loading ? 'Generating...' : 'Generate Wanted Poster' }}
        </button>
      </div>

      <!-- only shows if something went wrong -->
      <div v-if="error" class="error">{{ error }}</div>

      <!-- poster output - only renders once we have data back from the backend -->
      <div v-if="poster" class="poster">

        <!-- classic wanted poster header -->
        <div class="poster-header">
          <p class="wanted-text">WANTED</p>
          <p class="dead-or-alive">DEAD OR ALIVE</p>
        </div>

        <!-- mugshot area - shows uploaded photo or a placeholder -->
        <div class="mugshot">
          <img v-if="poster.portrait_url" :src="poster.portrait_url" class="mugshot-photo" />
          <img v-else-if="uploadedPhoto" :src="uploadedPhoto" class="mugshot-photo" />
          <div v-else class="mugshot-placeholder">
            <p>🗡️</p>
            <p>No Photo</p>
          </div>
        </div>

        <!-- character name and AI generated alias -->
        <div class="poster-name">
          <h2>{{ form.name }}</h2>
          <p class="alias">Also known as "{{ poster.alias }}"</p>
        </div>

        <!-- main poster body with AI generated text and character details -->
        <div class="poster-body">
          <!-- dramatic old English description from the AI -->
          <p class="poster-text">{{ poster.poster_text }}</p>

          <!-- character stats pulled from the form -->
          <div class="poster-details">
            <p><span>Race:</span> {{ form.race }}</p>
            <p><span>Class:</span> {{ form.charClass }}</p>
            <p><span>Last Seen:</span> {{ form.location }}</p>
            <p><span>Threat Level:</span> {{ poster.threat_level }}</p>
          </div>

          <!-- crimes listed in a bordered box -->
          <div class="crimes-section">
            <p class="crimes-title">CRIMES:</p>
            <p>{{ form.crimes }}</p>
          </div>

          <!-- AI generated warning for bounty hunters -->
          <div class="caution-section">
            <p>{{ poster.caution }}</p>
          </div>
        </div>

        <!-- bounty amount at the bottom of the poster -->
        <div class="poster-footer">
          <p class="bounty-label">BOUNTY</p>
          <p class="bounty-amount">{{ poster.bounty }}</p>
          <p class="contact">Contact your local Guard or Adventurers Guild</p>
        </div>
        <!-- reset button to clear the form and generate a new poster -->
        <button class="generate-another" @click="generateAnother">
        Generate Another
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// tracks loading state, errors, and the generated poster output
const loading = ref(false)
const error = ref('')
const poster = ref<any>(null)

// stores the uploaded photo as base64 for display on the poster
const uploadedPhoto = ref<string | null>(null)

// form data for the wanted character bound to inputs via v-model
const form = reactive({
  name: '',
  race: '',
  charClass: '',
  description: '',
  crimes: '',
  location: ''
})

// reads the uploaded image file and converts it to base64
function handlePhotoUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedPhoto.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

// sends character details to the FastAPI backend and gets back
// an AI-generated wanted poster with bounty, threat level, and old English flair
async function generatePoster() {
  loading.value = true
  error.value = ''
  poster.value = null

  try {
    const res = await fetch('http://127.0.0.1:8000/generate_poster', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.name,
        race: form.race,
        char_class: form.charClass, // snake_case for Python backend
        description: form.description,
        crimes: form.crimes,
        location: form.location,
        photo: uploadedPhoto.value || null // send photo if uploaded
      })
    })

    if (!res.ok) throw new Error(`Server error: ${res.status}`)
    poster.value = await res.json()
  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// resets the form and poster so the user can generate a new one
function generateAnother() {
  poster.value = null
  uploadedPhoto.value = null
  error.value = ''
  form.name = ''
  form.race = ''
  form.charClass = ''
  form.description = ''
  form.crimes = ''
  form.location = ''
}
</script>

<style scoped>
/* overall app wrapper dark fantasy background */
.app {
  font-family: serif;
  min-height: 100vh;
  background-color: #1a1a2e;
  color: #f0e6d3;
  padding: 20px;
}

/* centered header with gold title */
header {
  text-align: center;
  padding: 30px 0;
}

header h1 {
  font-size: 2.5rem;
  color: #c9a84c;
}

header p {
  color: #a89070;
}

/* form container */
.form-card {
  max-width: 600px;
  margin: 0 auto;
  background: #2a1f14;
  padding: 30px;
  border-radius: 8px;
  border: 2px solid #c9a84c;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* each input group stacks label above input */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  color: #c9a84c;
  font-weight: bold;
}

/* inputs styled to match the dark fantasy theme */
input, textarea {
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #c9a84c;
  background: #1a1a2e;
  color: #f0e6d3;
  font-family: serif;
  font-size: 14px;
}

/* generate button gold to match the theme */
button {
  padding: 15px;
  background: #c9a84c;
  color: #1a1a2e;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  font-family: serif;
}

/* dims the button while the API call is in progress */
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* file input for optional photo upload */
.file-input {
  padding: 8px;
  border: 1px solid #c9a84c;
  border-radius: 5px;
  background: #1a1a2e;
  color: #f0e6d3;
  cursor: pointer;
}

.optional-note {
  font-size: 0.8rem;
  color: #a89070;
  margin: 0;
  font-style: italic;
}

/* small preview of the uploaded photo in the form */
.photo-preview {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 5px;
  border: 2px solid #c9a84c;
  margin-top: 8px;
}

/* error message if the API call fails */
.error {
  color: red;
  text-align: center;
  margin-top: 20px;
}

/* the actual wanted poster*/
.poster {
  max-width: 600px;
  margin: 30px auto;
  background: #f5e6c8;
  color: #2a1a0a;
  border: 8px solid #8b4513;
  border-radius: 4px;
  padding: 30px;
  text-align: center;
  font-family: serif;
}

/* big red WANTED text at the top */
.wanted-text {
  font-size: 3rem;
  font-weight: bold;
  letter-spacing: 10px;
  color: #8b0000;
  margin: 0;
}

.dead-or-alive {
  font-size: 1.2rem;
  letter-spacing: 5px;
  margin: 0;
  color: #2a1a0a;
}

/* mugshot box shows uploaded photo or sword placeholder */
.mugshot {
  width: 150px;
  height: 180px;
  margin: 15px auto;
  border: 4px solid #8b4513;
  overflow: hidden;
  background: #d4c5a9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mugshot-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* placeholder shown when no photo is uploaded */
.mugshot-placeholder {
  text-align: center;
  color: #8b4513;
  font-size: 2rem;
}

.poster-name h2 {
  font-size: 2rem;
  margin: 15px 0 5px 0;
  color: #2a1a0a;
}

/* AI generated alias in italics */
.alias {
  font-style: italic;
  color: #5a3a1a;
}

.poster-body {
  text-align: left;
  margin: 20px 0;
}

/* dramatic AI generated description */
.poster-text {
  font-style: italic;
  margin-bottom: 15px;
  line-height: 1.6;
}

.poster-details p {
  margin: 5px 0;
}

.poster-details span {
  font-weight: bold;
}

/* crimes listed in a bordered section */
.crimes-section {
  margin-top: 15px;
  padding: 10px;
  border: 1px solid #8b4513;
}

.crimes-title {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 5px;
}

/* red warning box for the bounty hunter caution */
.caution-section {
  margin-top: 15px;
  padding: 10px;
  background: #8b0000;
  color: #f5e6c8;
  border-radius: 4px;
}

/* footer with the bounty amount */
.poster-footer {
  margin-top: 20px;
  border-top: 2px solid #8b4513;
  padding-top: 15px;
}

.bounty-label {
  font-size: 1rem;
  letter-spacing: 3px;
  margin: 0;
}

.bounty-amount {
  font-size: 2rem;
  font-weight: bold;
  color: #8b0000;
  margin: 5px 0;
}

.contact {
  font-size: 0.8rem;
  font-style: italic;
  color: #5a3a1a;
}

/* generate another button */
.generate-another {
  margin-top: 20px;
  background: #8b4513;
  color: #f5e6c8;
  width: 100%;
}

.generate-another:hover {
  background: #6b3410;
}
</style>