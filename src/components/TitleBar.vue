<script setup lang="ts">
import { Minus, Square, X } from 'lucide-vue-next'
import { logoUrl } from '@/assets'
const api = window.qlu
</script>

<template>
  <header class="titlebar">
    <div class="titlebar-drag"><span class="app-dot"><img :src="logoUrl" alt="" /></span><span>QLU 工具箱</span></div>
    <div class="window-controls">
      <button aria-label="最小化" @click="api.windowAction('minimize')"><Minus :size="15" /></button>
      <button aria-label="最大化" @click="api.windowAction('maximize')"><Square :size="13" /></button>
      <button class="window-close" aria-label="关闭" @click="api.windowAction('close')"><X :size="16" /></button>
    </div>
  </header>
</template>
