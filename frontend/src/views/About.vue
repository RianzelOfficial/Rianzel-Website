<template>
  <div class="container py-5">
    <div class="row">
      <div class="col-md-12">
        <h1 class="text-center mb-4">About Us</h1>
        <div class="card shadow-sm">
          <div class="card-body">
            <h2 class="card-title">Our Story</h2>
            <p class="card-text">
              Welcome to Rianzel Official Website! We are dedicated to providing high-quality content and services to our community.
            </p>
            <h3 class="mt-4">Our Mission</h3>
            <p>
              Our mission is to create a platform where people can connect, learn, and grow together.
            </p>
            <h3 class="mt-4">Our Team</h3>
            <div class="row mt-4">
              <div class="col-md-4" v-for="member in teamMembers" :key="member.id">
                <div class="card team-member-card">
                  <img :src="member.avatar" class="card-img-top" alt="Team Member">
                  <div class="card-body">
                    <h5 class="card-title">{{ member.name }}</h5>
                    <p class="card-text">{{ member.role }}</p>
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
  name: 'About',
  data() {
    return {
      teamMembers: [
        {
          id: 1,
          name: 'Rianzel',
          role: 'Founder',
          avatar: 'https://via.placeholder.com/300'
        },
        {
          id: 2,
          name: 'John Doe',
          role: 'Developer',
          avatar: 'https://via.placeholder.com/300'
        },
        {
          id: 3,
          name: 'Jane Smith',
          role: 'Designer',
          avatar: 'https://via.placeholder.com/300'
        }
      ]
    }
  }
}
</script>

<style scoped>
.team-member-card {
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}

.team-member-card:hover {
  transform: translateY(-5px);
}

.card-img-top {
  height: 200px;
  object-fit: cover;
}
</style>
