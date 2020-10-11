<template>
  <transition
    name="vertical-slide-fade"
    mode="out-in"
    @beforeLeave="beforeLeave"
    @enter="enter"
    @afterEnter="afterEnter"
  >
    <slot />
  </transition>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

@Component
export default class VerticalSlideFade extends Vue {
  public prevHeight = 'auto';

  public beforeLeave(element: HTMLElement) {
    this.prevHeight = getComputedStyle(element).height;
  }

  public enter(element: HTMLElement) {
    const { height } = getComputedStyle(element);

    element.style.height = this.prevHeight;

    setTimeout(() => {
      element.style.height = height;
    });
  }

  public afterEnter(element: HTMLElement) {
    element.style.height = 'auto';
  }
}
</script>

<style scoped>
.vertical-slide-fade-enter-active,
.vertical-slide-fade-leave-active {
  transition-duration: 0.5s;
  transition-property: height, opacity, transform;
  transition-timing-function: ease;
  overflow: hidden;
}

.vertical-slide-fade-enter {
  transform: translateY(-50px);
  opacity: 0;
}

.vertical-slide-fade-leave-to {
  transform: translateY(50px);
  opacity: 0;
}
</style>
