from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from blog.models import Post, Category, Tag
from .adminforms import PostAdminForm
from django.contrib import admin
from typeidea.custom_site import custom_site


# Register your models here.

class PostInline(admin.TabularInline):  # StacuedInline样式不同
    fields = ('title', 'desc')
    extra = 1  # 控制额外多几个
    model = Post


# @admin.register(Category)
@admin.register(Category, site=custom_site)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [PostInline]
    list_display = ['name', 'owner', 'status', 'is_nav', 'created_time', 'post_count']
    fields = ['name', 'status', 'is_nav']  # 控制admin后台显示的字段

    # 因为当前所有的用户都可以随意把自己创建的内容改为其他的作者，所以重写save_model方法，把owner这个字段设定为当前的登录用户
    # 如果fields字段设置显示owner，那在后再管理中会看到所有的注册用户名称，但是在创建分类时就算选择其他用户在保存时还是会保存当前的用户
    # 所以安全在owner可以选择不显示，增加分类时自动保存当前登录用户
    def save_model(self, request, obj, form, change):
        """
        :param request:  当前的请求
        :param obj: 当前要保存的对象
        :param form:  form是页面提交过来的表单之后的对象
        :param change: change用于报纸本次保存的数据是新增的还是更新的
        :return:
        """
        obj.owner = request.user  # request.user是当前登录的用户，如果是未登录的情况下，request.user拿到是匿名对象
        return super(CategoryAdmin, self).save_model(request, obj, form, change)

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


# @admin.register(Tag)
@admin.register(Tag, site=custom_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'created_time']
    fields = ['name', 'status']

    # 因为当前所有的用户都可以随意把自己创建的内容改为其他的作者，所以重写save_model方法，把owner这个字段设定为当前的登录用户
    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


class CategoryOwnerFilter(admin.SimpleListFilter):
    """
     自定义过滤器只展示当前用户分类

     SimpleListFilter类提供了两个属性和两个方法来供我们重写,
     两个属性:
        title：‘用于展示标题’
        parameter_name: 是查询URL参数的名字, 比如查询分类id为1的内容时,URL后面的query部分是 ?owner_category=2, 此时就可以通过过滤器
                        拿到这个id，从而进行过滤
    两个方法:
        lookups: 返回要展示的内容和查询用的id ( 就是上面query用的)
        queryset: 根据URL Query的内容返回列表页数据,
    """
    title = '分类过滤器'
    parameter_name = "owner_category"

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset


# @admin.register(Post)
@admin.register(Post, site=custom_site)
class PostAdmin(admin.ModelAdmin):
    # 配置列表页展示字段
    list_display = [
        'title', 'category', 'status', 'created_time', 'operator', 'owner'
    ]  # operator 自定义一个操作字段

    # 配置那些字段可以作为链接，点击可以进入编辑页面
    list_display_links = []

    # list_filter = ['category']  # 显示过滤器，根据那些字段进行过滤
    list_filter = [CategoryOwnerFilter]  # 显示过滤器，根据那些字段进行过滤
    search_fields = ['title', 'category__name']  # 显示搜索栏，可以根据那些字段进行搜索

    # actions_on_top = True  # 动作相关的配置，是否现在在顶部
    # actions_on_bottom = True  # 动作相关的配置，是否现在在底部

    # 编辑页面
    # save_on_top = True  # 保存，编辑，编辑及新建按钮是否在顶部展示，默认在底部展示

    # exclude = ('owner', )

    # fields两个作用, 一个是限定要展示的字段, 另外一个是配置展示字段的顺序, fields与fieldset任选其一
    # fields = [
    #     'category', 'title', 'desc', 'status', 'content', 'tag'
    # ]

    # fieldsets用来控制全局
    # fieldsets格式： 第一个元素是string, 第二个元素是dict, dict的key可以是'fileds'/ description / classes
    #                fields控制展示那些元素, classes是给要配置的版块加上一些css属性, django admin默认支持collapse、wide
    # fieldsets = (
    #     ('名称', {'内容'}),
    #     ('名称', {'内容'})
    # )
    fieldsets = (
        (
            "基础配置", {
                "description": "基础配置描述",
                "fields": (
                    ('title', 'category'),  # 元组带面两个字段显示为一行
                    'status',
                )
            }
        ),
        (
            '内容', {
                'fields': (
                    'desc',
                    'content',
                )
            }
        ),
        (
            '额外信息', {
                'classes': ('collapse',),
                'fields': ('tag',),
            }
        )
    )

    # filter_horizontal = ('tag', )
    # filter_vertical = ('tag', )

    # form = PostAdminForm  # 摘要多行多列展示

    def operator(self, obj):
        return format_html(
            "<a href='{}'>编辑</a>",
            # reverse('admin:blog_post_change', args=(obj.id,))
            reverse('cus_admin:blog_post_change', args=(obj.id,))
        )

    operator.short_description = '操作'  # 自定义字段的描述信息

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    class Meta:
        css = {
            'all': ('https://bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css',),
        }
        js = ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js',)
