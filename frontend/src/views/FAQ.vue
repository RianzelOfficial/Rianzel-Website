<template>
  <div class="faq-page container mt-5">
    <div class="row">
      <div class="col-12">
        <h1 class="mb-4 text-center">Frequently Asked Questions (FAQ)</h1>
      </div>
    </div>

    <div class="accordion" id="faqAccordion">
      <div class="accordion-item" v-for="(item, index) in faqItems" :key="index">
        <h2 class="accordion-header" :id="'heading' + index">
          <button class="accordion-button" :class="{ collapsed: activeAccordion !== index }" type="button" @click="toggleAccordion(index)">
            {{ item.question }}
          </button>
        </h2>
        <div :id="'collapse' + index" class="accordion-collapse collapse" :class="{ show: activeAccordion === index }" :aria-labelledby="'heading' + index" data-bs-parent="#faqAccordion">
          <div class="accordion-body">
            <p v-html="item.answer"></p>
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-5">
      <div class="col-12 text-center">
        <h4>Still have questions?</h4>
        <p>If you can't find the answer you're looking for, feel free to <router-link to="/contact">contact us</router-link>.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'FAQ',
  setup() {
    const activeAccordion = ref(null);

    const faqItems = ref([
      {
        question: 'How do I register for an account?',
        answer: 'To register for an account, click on the "Register" link in the top navigation bar. Fill out the required information, including your desired username, email address, and password. Once submitted, you may need to verify your email address to activate your account.'
      },
      {
        question: 'How can I create a new post in the forum?',
        answer: 'To create a new post, you must first be logged in. Navigate to the forum section and choose a relevant category. Click on the "Create New Topic" button, fill in the title and content of your post, and then submit it. Your post will then be visible to other users.'
      },
      {
        question: 'Can I edit or delete my posts?',
        answer: 'Yes, you can typically edit or delete your own posts. Look for an "Edit" or "Delete" option next to your post. Please note that some forums may have time limits for editing or specific rules regarding post deletion.'
      },
      {
        question: 'What are the community guidelines?',
        answer: 'Our community guidelines are designed to ensure a positive and respectful environment for all users. Generally, this includes refraining from offensive language, spam, personal attacks, and illegal content. Please refer to the dedicated "Community Guidelines" page (if available) or contact a moderator for detailed information.'
      },
      {
        question: 'How do I reset my password?',
        answer: 'If you\'ve forgotten your password, click on the "Login" link and then select the "Forgot Password?" option. You will be prompted to enter your email address, and instructions for resetting your password will be sent to you.'
      },
      {
        question: 'Who can I contact for support?',
        answer: 'If you need support or have questions not covered in this FAQ, please use the <router-link to="/contact">Contact Us</router-link> page. We will do our best to assist you as soon as possible.'
      }
    ]);

    const toggleAccordion = (index) => {
      if (activeAccordion.value === index) {
        activeAccordion.value = null;
      } else {
        activeAccordion.value = index;
      }
    };

    return {
      faqItems,
      activeAccordion,
      toggleAccordion
    };
  }
};
</script>

<style scoped>
.faq-page {
  max-width: 800px;
  margin: auto;
}

.accordion-button:not(.collapsed) {
  color: var(--bs-primary);
  background-color: var(--bs-accordion-active-bg);
}

.accordion-button:focus {
  box-shadow: none;
  border-color: rgba(0,0,0,.125);
}

.accordion-item {
  margin-bottom: 1rem;
  border: 1px solid rgba(0,0,0,.125);
  border-radius: .25rem;
}

.accordion-header {
  margin-bottom: 0;
}

.accordion-body p:last-child {
  margin-bottom: 0;
}
</style>
