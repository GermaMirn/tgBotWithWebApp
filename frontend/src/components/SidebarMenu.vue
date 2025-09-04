<template>
  <div class="sidebar-container">
    <!-- Кнопка бургер-меню с анимированной иконкой -->
    <Button
      @click="toggleMenu"
      class="burger-button"
      text
      rounded
    >
      <span class="burger-svg" :class="{ open: visible }">
        <span></span>
        <span></span>
        <span></span>
      </span>
    </Button>

    <!-- Overlay для блокировки скролла -->
    <Transition name="overlay">
      <div
        v-if="visible"
        class="sidebar-overlay"
        @click="toggleMenu"
      ></div>
    </Transition>

    <!-- Боковое меню -->
    <Transition name="sidebar">
      <div
        v-if="visible"
        class="sidebar-menu"
      >
        <div class="sidebar-content">
          <div class="sidebar-header">
            <h2>Языковая студия</h2>
            <p>Английский и китайский</p>
          </div>

          <nav class="sidebar-nav">
            <ul class="nav-list">
              <li class="nav-item">
                <router-link
                  to="/home"
                  class="nav-link"
                  @click="toggleMenu"
                  active-class="active"
                >
                  <i class="pi pi-home"></i>
                  <span>Главная</span>
                </router-link>
              </li>

              <li class="nav-item">
                <router-link
                  to="/profile"
                  class="nav-link"
                  @click="toggleMenu"
                  active-class="active"
                >
                  <i class="pi pi-user"></i>
                  <span>Мой профиль</span>
                </router-link>
              </li>

              <li class="nav-item">
                <router-link
                  to="/groups"
                  class="nav-link"
                  @click="toggleMenu"
                  active-class="active"
                >
                  <i class="pi pi-users"></i>
                  <span>Группы</span>
                </router-link>
              </li>

              <li class="nav-item">
                <router-link
                  to="/calendar"
                  class="nav-link"
                  @click="toggleMenu"
                  active-class="active"
                >
                  <i class="pi pi-calendar"></i>
                  <span>Календарь занятий</span>
                </router-link>
              </li>

              <li class="nav-item">
                <router-link
                  to="/teachers"
                  class="nav-link"
                  @click="toggleMenu"
                  active-class="active"
                >
                  <i class="pi pi-graduation-cap"></i>
                  <span>Преподаватели</span>
                </router-link>
              </li>

              <!-- Пункт меню только для админов -->
              <li v-if="isAdmin" class="nav-item">
                <router-link
                  to="/admin/role-switch"
                  class="nav-link"
                  @click="toggleMenu"
                  active-class="active"
                >
                  <i class="pi pi-key"></i>
                  <span>Управление ролями</span>
                </router-link>
              </li>
            </ul>
          </nav>

          <div class="sidebar-footer">
            <div class="user-info" v-if="userStore.isAuthenticated">
              <Avatar
                :label="userStore.userData?.full_name?.charAt(0) || 'U'"
                shape="circle"
                size="normal"
              />
              <div class="user-details">
                <p class="user-name">{{ userStore.userData?.full_name || 'Пользователь' }}</p>
                <p class="user-role">{{ getUserRoleName() }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

    </Transition>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useUserStore } from '@/stores/user'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'

export default defineComponent({
  name: 'SidebarMenu',
  components: { Button, Avatar },
  data() {
    return {
      visible: false,
      userStore: useUserStore(),
    }
  },
  computed: {
    isAdmin(): boolean {
      return this.userStore.isAdmin
    }
  },
  methods: {
    getUserRoleName() {
      const role = this.userStore.userRole
      const roleNames: Record<string, string> = {
        admin: 'Администратор',
        teacher: 'Учитель',
        student: 'Студент'
      }
      return roleNames[role || 'student'] || 'Студент'
    },
    toggleMenu() {
      this.visible = !this.visible
      document.body.style.overflow = this.visible ? 'hidden' : 'auto'
    }
  }
})
</script>

<style scoped>
.sidebar-container {
  position: relative;
}

/* Overlay для затемнения и блокировки скролла */
.sidebar-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.4);
  z-index: 2000;
}

/* Анимация для overlay */
.overlay-enter-active, .overlay-leave-active {
  transition: opacity 0.2s;
}
.overlay-enter-from, .overlay-leave-to {
  opacity: 0;
}
.overlay-enter-to, .overlay-leave-from {
  opacity: 1;
}

/* Само меню */
.sidebar-menu {
  position: fixed;
  top: 0; left: 0;
  width: 100vw;
  height: 100vh;
  background: var(--surface-card, #fff);
  z-index: 2100;
  display: flex;
  flex-direction: column;
}

/* Анимация для меню */
.sidebar-enter-active, .sidebar-leave-active {
  transition: transform 0.25s cubic-bezier(.4,0,.2,1), opacity 0.2s;
}
.sidebar-enter-from, .sidebar-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
.sidebar-enter-to, .sidebar-leave-from {
  transform: translateX(0);
  opacity: 1;
}

/* Анимация смены иконки */
.burger-svg {
  display: inline-block;
  width: 24px;
  height: 24px;
  position: relative;
  transition: all 0.3s;
  cursor: pointer;
}
.burger-svg span {
  display: block;
  position: absolute;
  height: 3px;
  width: 100%;
  background: #222;
  border-radius: 2px;
  opacity: 1;
  left: 0;
  transition: all 0.3s;
}
.burger-svg span:nth-child(1) {
  top: 4px;
}
.burger-svg span:nth-child(2) {
  top: 10px;
}
.burger-svg span:nth-child(3) {
  top: 16px;
}
.burger-svg.open span:nth-child(1) {
  top: 10px;
  transform: rotate(45deg);
}
.burger-svg.open span:nth-child(2) {
  opacity: 0;
}
.burger-svg.open span:nth-child(3) {
  top: 10px;
  transform: rotate(-45deg);
}
.burger-button {
  /* ...оставьте ваши стили, но уменьшите размер если нужно... */
  width: 2.3rem;
  height: 2.3rem;
  min-width: unset;
  min-height: unset;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
}

.sidebar-header {
  padding: 1.2rem 1rem 0.7rem 1rem;
  border-bottom: 1px solid var(--surface-border);
  text-align: center;
  background: var(--surface-card);
  flex-shrink: 0;
  position: relative;
}

.sidebar-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 1.2rem;
  font-weight: 600;
}

.sidebar-header p {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.burger-button {
  position: fixed;
  top: 0.7rem;
  left: 0.7rem;
  z-index: 3000;
  background: var(--surface-card) !important;
  border: 1px solid var(--surface-border) !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 2.3rem;
  height: 2.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.burger-button i {
  font-size: 1.3rem;
  color: #222 !important;
}

.burger-button:hover {
  background: var(--surface-hover) !important;
  transform: scale(1.05);
  transition: all 0.2s ease;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 1.2rem 0;
  padding-bottom: 100px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  color: var(--text-color);
  text-decoration: none;
  transition: all 0.2s ease;
  border-radius: 0;
  font-size: 1.1rem;
  border-bottom: 1px solid var(--surface-border);
}

.nav-link:hover {
  background: var(--surface-hover);
  color: var(--primary-color);
  transform: translateX(5px);
}

.nav-link.active {
  background: var(--primary-color);
  color: var(--primary-color-text);
}

.nav-link i {
  margin-right: 1.2rem;
  font-size: 1.2rem;
  width: 1.7rem;
  text-align: center;
}

.nav-link span {
  font-size: 1.1rem;
  font-weight: 500;
}

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  border-top: 1px solid var(--surface-border);
  background: var(--surface-card);
  flex-shrink: 0;
  height: 80px;
}

.user-info {
  display: flex;
  align-items: center;
  height: 100%;
}

.user-details {
  margin-left: 0.7rem;
}

.user-name {
  margin: 0 0 0.25rem 0;
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.95rem;
}

.user-role {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: 0.85rem;
}

/* Адаптация под мобильные устройства */
@media (max-width: 768px) {
  .burger-button {
    top: 0.5rem;
    left: 0.5rem;
    width: 2.7rem;
    height: 2.7rem;
  }

  .burger-button i {
    font-size: 1.5rem;
  }

  .nav-link {
    padding: 1.2rem 1.5rem;
    font-size: 1.15rem;
  }

  .nav-link i {
    font-size: 1.3rem;
    margin-right: 1.2rem;
  }

  .nav-link span {
    font-size: 1.15rem;
  }

  .sidebar-header h2 {
    font-size: 1.3rem;
  }

  .sidebar-header p {
    font-size: 1rem;
  }

  .sidebar-footer {
    height: 100px;
    padding: 1.2rem 1rem;
  }

  .sidebar-nav {
    padding-bottom: 110px;
  }
}
</style>
