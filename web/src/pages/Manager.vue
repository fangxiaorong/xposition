<template>
  <div>
    <v-toolbar flat color="white">
      <v-toolbar-title>后台用户</v-toolbar-title>
      <v-divider class="mx-2" inset vertical></v-divider>
      <v-spacer></v-spacer>
      <v-dialog v-model="dialog" max-width="800px">
        <v-btn slot="activator" color="primary" dark class="mb-2">新增</v-btn>
        <v-card>
          <v-card-title>
            <span class="headline">{{ formTitle }}</span>
          </v-card-title>

          <v-card-text>
            <v-container grid-list-md>
              <v-layout wrap>
                <v-flex xs12 sm6 md6>
                  <v-text-field v-model="editedItem.username" label="用户名"></v-text-field>
                </v-flex>
                <v-flex xs12 sm6 md6>
                  <v-text-field v-model="editedItem.nickname" label="昵称"></v-text-field>
                </v-flex>
                <v-flex xs12 sm6 md6>
                  <v-text-field v-model="editedItem.password" type="password" label="密码"></v-text-field>
                </v-flex>
                <v-flex xs12 sm6 md6>
                  <v-text-field v-model="editedItem.repassword" type="password" label="确认密码"></v-text-field>
                </v-flex>
              </v-layout>
            </v-container>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" flat @click.native="close">取消</v-btn>
            <v-btn color="blue darken-1" flat @click.native="save">保存</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-toolbar>
    <v-data-table :headers="headers" :items="users" hide-actions>
      <template slot="items" slot-scope="props">
        <td>{{ props.item.id }}</td>
        <td>{{ props.item.username }}</td>
        <td>{{ props.item.nickname }}</td>
        <td>{{ props.item.create_time }}</td>
        <td>{{ props.item.update_time }}</td>
        <td>
          <v-icon small class="mr-2" @click="editItem(props.item)">
            edit
          </v-icon>
          <v-icon small @click="deleteItem(props.item)">
            delete
          </v-icon>
        </td>
      </template>
      <template slot="no-data">
        <h1>暂无用户</h1>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import md5 from 'js-md5';
export default {
  data: () => ({
    dialog: false,
    headers: [
      { text: 'ID', value: 'name', sortable: false, align: 'left' },
      { text: '用户名', value: 'calories', sortable: false },
      { text: '昵称', value: 'fat', sortable: false },
      { text: '创建时间', value: 'carbs', sortable: false },
      { text: '更新时间', value: 'protein', sortable: false },
      { text: '动作', value: 'name', sortable: false }
    ],
    users: [
    ],
    editedIndex: -1,
    editedItem: {
      username: '',
      nickname: '',
      password: '',
      repassword: '',
    },
  }),
  computed: {
    formTitle () {
      return this.editedIndex === -1 ? '新增' : '编辑';
    },
  },
  watch: {
    dialog (val) {
      val || this.close();
    },
  },
  created () {
    this.initialize();
  },
  methods: {
    initialize () {
      this.axios.get('/api/admin/user/list').then((response) => {
        if (response.data.state === 1) {
          this.users = response.data.users;
        } else {
          console.log(response.data.message);
        }
      });
    },

    editItem (item) {
      this.editedIndex = this.users.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },

    deleteItem (item) {
      const index = this.users.indexOf(item);
      if (confirm('是否确认删除此用户?')) {
        this.users.splice(index, 1);
      }
    },

    close () {
      this.dialog = false;
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      }, 300);
    },

    save () {
      if (this.editedItem.username.trim() === '' || this.editedItem.password.trim() === '') {
        alert('用户名/密码不能为空');
      } else if (this.editedItem.password.trim() !== this.editedItem.repassword.trim()) {
        alert('密码不相同');
      } else {
        if (this.editedIndex > -1) {
          Object.assign(this.users[this.editedIndex], this.editedItem);
        } else {
          let data = 'username=' + this.editedItem.username.trim() + '&nickname=' + encodeURI(this.editedItem.nickname.trim()) + '&password=' + md5(this.editedItem.password.trim());
          this.axios.post('/api/admin/user/add', data).then((response) => {
            // console.log(response);
            this.initialize();
          });
        }
        this.close();
      }
    },
    pathSelected (item) {
      this.selected = item;
    },
  }
};
</script>
