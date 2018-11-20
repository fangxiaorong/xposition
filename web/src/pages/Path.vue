<template>
  <div>
    <v-container grid-list-xl fluid>
      <v-layout row wrap>
        <v-flex lg3>
          <v-card>
            <v-list>
              <v-list-tile v-for="item in items" :key="item.id" @click="pathSelected(item)">
                <v-list-tile-action>
                  <v-checkbox off-icon="bookmark" on-icon="bookmark_border">star</v-checkbox>
                </v-list-tile-action>

                <v-list-tile-content>
                  <v-list-tile-title v-text="item.name"></v-list-tile-title>
                </v-list-tile-content>
              </v-list-tile>

              <v-dialog v-model="pathDialog" max-width="800px">
                <v-btn slot="activator" color="primary" dark class="mb-2">新增</v-btn>
                <v-card>
                  <v-card-title>
                    <span class="headline">新建路径</span>
                  </v-card-title>
                  <v-card-text>
                    <v-text-field v-model="pathname" label="路径名称"></v-text-field>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat @click.native="exitPath">取消</v-btn>
                    <v-btn color="blue darken-1" flat @click.native="newPath">保存</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>

            </v-list>
          </v-card>
          
        </v-flex>
        <v-flex lg9 v-if="selected">
          <v-toolbar flat color="white">
            <v-toolbar-title>{{ selected.name }}</v-toolbar-title>
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
                        <v-text-field v-model="editedItem.x" label="X"></v-text-field>
                      </v-flex>
                      <v-flex xs12 sm6 md6>
                        <v-text-field v-model="editedItem.y" label="Y"></v-text-field>
                      </v-flex>
                      <v-flex xs12 sm6 md4>
                        <v-text-field v-model="editedItem.leve1" label="高"></v-text-field>
                      </v-flex>
                      <v-flex xs12 sm6 md4>
                        <v-text-field v-model="editedItem.leve2" label="中"></v-text-field>
                      </v-flex>
                      <v-flex xs12 sm6 md4>
                        <v-text-field v-model="editedItem.leve3" label="低"></v-text-field>
                      </v-flex>
                      <v-flex xs12 sm6 md6>
                        <!-- <v-checkbox v-model="editedItem.senable" label="开始时间"></v-checkbox> -->
                        <v-text-field v-model="editedItem.stime" />
                        <!-- <v-time-picker v-model="editedItem.stime" class="mt-3" format="24hr" :readonly="!editedItem.senable" /> -->
                      </v-flex>
                      <v-flex xs12 sm6 md6>
                        <!-- <v-checkbox v-model="editedItem.eenable" label="结束时间"></v-checkbox> -->
                        <v-text-field v-model="editedItem.etime" />
                        <!-- <v-time-picker v-model="editedItem.etime" class="mt-3" format="24hr" :readonly="!editedItem.eenable" /> -->
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
          <v-data-table :headers="headers" :items="desserts" hide-actions>
            <template slot="items" slot-scope="props">
              <!-- <td>{{ props.item.order }}</td> -->
              <td>{{ props.item.x }}</td>
              <td>{{ props.item.y }}</td>
              <td>{{ props.item.level1 }}</td>
              <td>{{ props.item.level2 }}</td>
              <td>{{ props.item.level3 }}</td>
              <td>{{ props.item.stime }}</td>
              <td>{{ props.item.etime }}</td>
              <td>
                <v-icon small class="mr-2" @click="editItem(props.item)">
                  edit
                </v-icon>
                <v-icon small @click="deleteItem(props.item)">
                  delete
                </v-icon>
              </td>
            </template>
          </v-data-table>
          <div class="text-xs-right">
            <v-btn color="primary" @click="saveExamLine">保存</v-btn>
          </div>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
export default {
  data: () => ({
    selected: undefined,
    pathDialog: false,
    pathname: '',
    items: [],
    dialog: false,
    headers: [
      // { text: '序号', value: 'name', sortable: false, align: 'left' },
      { text: 'X', value: 'calories', sortable: false },
      { text: 'Y', value: 'fat', sortable: false },
      { text: '高', value: 'calories', sortable: false },
      { text: '中', value: 'calories', sortable: false },
      { text: '低', value: 'calories', sortable: false },
      { text: '开始时间', value: 'carbs', sortable: false },
      { text: '结束时间', value: 'carbs', sortable: false },
      { text: '动作', value: 'name', sortable: false }
    ],
    desserts: [],
    editedIndex: -1,
    editedItem: {
      x: '',
      y: '',
      level1: '',
      level2: '',
      level3: '',
      stime: '',
      etime: '',
      senable: false,
      eenable: false,
    },
    defaultItem: {
      x: '',
      y: '',
      level1: '',
      level2: '',
      level3: '',
      stime: '',
      etime: '',
      senable: false,
      eenable: false,
    }
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
      this.axios.get('/api/admin/examline/list').then((response) => {
        if (response.data.state === 1) {
          this.items = response.data.exam_line;
        }
      });
    },

    editItem (item) {
      this.editedIndex = this.desserts.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },

    deleteItem (item) {
      const index = this.desserts.indexOf(item);
      confirm('是否删除此点?') && this.desserts.splice(index, 1);
    },

    close () {
      this.dialog = false;
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      }, 300);
    },

    save () {
      if (this.editedIndex > -1) {
        Object.assign(this.desserts[this.editedIndex], this.editedItem);
      } else {
        this.desserts.push(this.editedItem);
      }
      this.close();
    },
    pathSelected (item) {
      this.selected = undefined;

      this.axios.get('/api/admin/examline?lineid=' + item.id).then((response) => {
        if (response.data.state === 1) {
          let data = response.data.exam_line;
          // data = data;
          this.selected = data;
        } else {
          alert(response.data.message);
        }
      });
    },
    exitPath () {
      this.editedItem = this.defaultItem;
      this.pathDialog = false;
    },
    newPath () {
      this.pathDialog = false;
      this.editedItem = this.defaultItem;

      if (this.pathname.trim() !== '') {
        this.axios.post('/api/admin/examline', 'name=' + this.pathname.trim()).then((response) => {
          if (response.data.state === 1) {
            this.initialize();
          } else {
            alert(response.data.message);
          }
        });
      } else {
        alert('路径名字不能为空!');
      }
    },
    saveExamLine () {
      console.log('');
    },
    enableStartTime () {
      console.log('xx');
    }
  }
};
</script>
