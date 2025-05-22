<template>
  <div class="container py-5">
    <div class="row">
      <div class="col-md-12">
        <h1 class="text-center mb-4">Contact Us</h1>
        <div class="row">
          <div class="col-md-6">
            <div class="card shadow-sm">
              <div class="card-body">
                <h2 class="card-title">Send us a Message</h2>
                <form @submit.prevent="sendMessage">
                  <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" class="form-control" id="name" v-model="formData.name" required>
                  </div>
                  <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" v-model="formData.email" required>
                  </div>
                  <div class="mb-3">
                    <label for="subject" class="form-label">Subject</label>
                    <input type="text" class="form-control" id="subject" v-model="formData.subject" required>
                  </div>
                  <div class="mb-3">
                    <label for="message" class="form-label">Message</label>
                    <textarea class="form-control" id="message" rows="5" v-model="formData.message" required></textarea>
                  </div>
                  <button type="submit" class="btn btn-primary">Send Message</button>
                </form>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card shadow-sm">
              <div class="card-body">
                <h2 class="card-title">Contact Information</h2>
                <div class="contact-info">
                  <div class="info-item mb-3">
                    <i class="fas fa-map-marker-alt"></i>
                    <p>123 Business Street, City, Country</p>
                  </div>
                  <div class="info-item mb-3">
                    <i class="fas fa-phone"></i>
                    <p>+1 234 567 8900</p>
                  </div>
                  <div class="info-item mb-3">
                    <i class="fas fa-envelope"></i>
                    <p>contact@rianzel.com</p>
                  </div>
                  <div class="info-item">
                    <i class="fas fa-clock"></i>
                    <p>Mon - Fri: 9:00 AM - 5:00 PM</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Contact',
  data() {
    return {
      formData: {
        name: '',
        email: '',
        subject: '',
        message: ''
      }
    }
  },
  methods: {
    async sendMessage() {
      try {
        // TODO: Implement actual message sending logic
        console.log('Sending message:', this.formData)
        // Reset form
        this.formData = {
          name: '',
          email: '',
          subject: '',
          message: ''
        }
        alert('Message sent successfully!')
      } catch (error) {
        console.error('Error sending message:', error)
        alert('Error sending message. Please try again.')
      }
    }
  }
}
</script>

<style scoped>
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.info-item i {
  color: var(--primary-color);
  font-size: 1.5rem;
  min-width: 30px;
}

.card {
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
}
</style>
