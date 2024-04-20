<template>
  <b-table :items="itemList" :fields="fields" striped hover variant="dark" class="table-dark">
    <template #header="{ header }">
      <th v-for="(key, index) in header.fields" :key="index">{{ key }}</th>
    </template>
    <template #cell="{ item, field }">
      <td>{{ item[field.key] }}</td>
    </template>
  </b-table>
</template>

<script>
export default {
  name: "custom-table",
  props: {
    itemList: {
      type: Array,
      required: true,
    },
  },
  computed: {
    fields() {
      const headers = new Set();
      for (const item of this.itemList) {
        Object.keys(item).forEach(key => headers.add(key));
      }
      return Array.from(headers).map(key => ({ key }));
    },
  },
};
</script>

<style scoped>
/* Add any table styling as needed */
</style>
