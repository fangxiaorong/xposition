<template>
  <div>
    <v-container grid-list-xl fluid>
      <v-layout row wrap>
        <v-flex lg3>
          <v-card>
            <v-list>
              <v-list-tile v-for="item in items" :key="item.id" @click="pathSelected(item)">
                <v-list-tile-action>
                  <v-checkbox off-icon="favorite" on-icon="favorite_border" v-model="item.valid" @change="updateState(item)">star</v-checkbox>
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
            <v-toolbar-title>{{ selected.name + (selected.valid ? '(有效)' : '(无效)') }}</v-toolbar-title>
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
                      <v-flex xs12 sm6 md3>
                        <v-text-field v-model="editedItem.x" label="X坐标"></v-text-field>
                      </v-flex>
                      <v-flex xs12 sm6 md3>
                        <v-text-field v-model="editedItem.y" label="Y坐标"></v-text-field>
                      </v-flex>
                      <v-flex xs12 sm6 md3>
                        <v-text-field v-model="editedItem.maxdistance" label="最大距离"></v-text-field>
                      </v-flex>
                      <v-flex xs12 sm6 md3>
                        <v-text-field v-model="editedItem.weight" label="权重"></v-text-field>
                      </v-flex>
                      <v-flex xs2 sm1 md1>
                        <v-checkbox v-model="editedItem.senable"></v-checkbox>
                      </v-flex>
                      <v-flex xs10 sm5 md5>
                        <v-text-field slot="activator" label="开始时间" v-model="editedItem.stime" append-icon="access_time" :readonly="!editedItem.senable"></v-text-field>
                      </v-flex>
                      <v-flex xs2 sm1 md1>
                        <v-checkbox v-model="editedItem.eenable"></v-checkbox>
                      </v-flex>
                      <v-flex xs10 sm5 md5>
                        <v-text-field slot="activator" label="结束时间" v-model="editedItem.etime" append-icon="access_time" :readonly="!editedItem.eenable"></v-text-field>
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
          <v-data-table :headers="headers" :items="selected.points || []" hide-actions>
            <template slot="items" slot-scope="props">
              <!-- <td>{{ props.item.order }}</td> -->
              <td>{{ props.item.x }}</td>
              <td>{{ props.item.y }}</td>
              <td>{{ props.item.maxdistance }}</td>
              <td>{{ props.item.weight }}</td>
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
            <template slot="no-data">
              <div></div>
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
      { text: '最大距离', value: 'calories', sortable: false },
      { text: '权重', value: 'calories', sortable: false },
      { text: '开始时间', value: 'carbs', sortable: false },
      { text: '结束时间', value: 'carbs', sortable: false },
      { text: '动作', value: 'name', sortable: false }
    ],
    editedIndex: -1,
    editedItem: {
      x: '',
      y: '',
      maxdistance: '',
      weight: 0,
      stime: '',
      etime: '',
      senable: false,
      eenable: false,
    },
    defaultItem: {
      x: '',
      y: '',
      maxdistance: '',
      weight: 0,
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
          this.items.forEach((item) => {
            item.valid = item.valid === 1 ? true : false;
          });
        }
      });
    },

    editItem (item) {
      this.editedIndex = this.selected.points.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },

    deleteItem (item) {
      const index = this.selected.points.indexOf(item);
      confirm('是否删除此点?') && this.selected.points.splice(index, 1);
    },

    close () {
      this.dialog = false;
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      }, 300);
    },

    save () {
      if (isNaN(parseFloat(this.editedItem.x)) || isNaN(parseFloat(this.editedItem.y)) || isNaN(parseFloat(this.editedItem.maxdistance))) {
        return alert('X，Y，最大距离必须是数字');
      }
      if (parseFloat(this.editedItem.maxdistance) <= 0) {
        return alert('最大距离必须大于0');
      }

      if (this.editedIndex > -1) {
        Object.assign(this.selected.points[this.editedIndex], this.editedItem);
      } else {
        this.selected.points.push(this.editedItem);
      }
      this.close();
    },
    pathSelected (item) {
      this.selected = undefined;

      this.axios.get('/api/admin/examline?lineid=' + item.id).then((response) => {
        if (response.data.state === 1) {
          let data = response.data.exam_line;
          data.points = JSON.parse(data.points) || [];
          data.valid = data.valid === 1 ? true : false;
          this.selected = data;
        } else {
          alert(response.data.message);
        }
      });
    },
    updateState (item) {
      console.log(item.valid);
      this.axios.post('/api/admin/examline', 'lineid=' + item.id + '&valid=' + (item.valid ? '1' : '2')).then((response) => {
        console.log(response.data);
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
        this.axios.post('/api/admin/examline', 'name=' + encodeURI(this.pathname.trim())).then((response) => {
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
      this.axios.post('/api/admin/examline', 'lineid=' + this.selected.id + '&points=' + JSON.stringify(this.selected.points)).then((response) => {
        if (response.data.state === 1) {
          window.alert('路径保存成功');
        } else {
          window.alert(response.data.message);
        }
      });
    }
  }
};
</script>
