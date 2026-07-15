<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, FileSpreadsheet, ArrowUpRight, ShieldCheck, Sparkles } from 'lucide-vue-next'
import PageHeader from '@/components/PageHeader.vue'
import type { BootstrapData, PageName } from '@/types'
const props = defineProps<{ data: BootstrapData }>()
const emit = defineEmits<{ navigate: [page: PageName] }>()
const query = ref('')
const visible = computed(() => !query.value || `${props.data.tool.name}${props.data.tool.description}`.toLowerCase().includes(query.value.toLowerCase()))
</script>
<template><div class="page"><PageHeader eyebrow="TOOLBOX" title="全部工具" description="为校园生活准备的一组轻量、本地化工具。"><label class="search-box"><Search :size="18" /><input v-model="query" placeholder="搜索工具…" /></label></PageHeader><div class="tool-grid"><article v-if="visible" class="tool-card featured" @click="emit('navigate', 'grade')"><div class="tool-card-top"><div class="tool-icon large excel"><FileSpreadsheet :size="25" /></div><span class="tool-version">v{{ data.tool.version }}</span></div><span class="category">{{ data.tool.category }}</span><h2>{{ data.tool.name }}</h2><p>{{ data.tool.description }}</p><div class="tool-meta"><span><ShieldCheck :size="15" /> 本地处理</span><span><Sparkles :size="15" /> 自动校验</span></div><button>打开工具 <ArrowUpRight :size="17" /></button></article><article class="tool-card coming"><div class="coming-mark">+</div><h2>更多工具正在路上</h2><p>工具箱会保持克制，只加入真正有用且经过安全评估的功能。</p></article></div></div></template>
