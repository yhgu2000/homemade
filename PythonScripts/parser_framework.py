################################################################################
#
# 版权所有 (c) 2019-2020 顾宇浩。保留所有权利。
#
# 文件: parser_framework.py
# 说明：这是我所有python指令脚本的参数解析框架
# 版本: v2.1 (2020-4-12)
#
################################################################################
#
#
from abc import ABC,abstractmethod

class InvalidOption(Exception):
    def __init__(self,msg:str):
        Exception.__init__(self,msg)
        return


class InvalidArgument(Exception):
    def __init__(self,msg:str):
        Exception.__init__(self,msg)
        return


class MissingArgument(Exception):
    def __init__(self,msg:str):
        Exception.__init__(self,msg)
        return


class UnexpectedArgument(Exception):
    def __init__(self,msg:str):
        Exception.__init__(self,msg)
        return


class Option(ABC):
    """选项参数类
    """
    def __init__(self,priority:int):
        """
        参数：
            priority:   优先级
                越小越优先。
                一次指令只会执行一个优先级非0的选项。
                建议将诸如'-r'类的环境选项定义为0，将'--auto'类的动作选项定义为
                正数，将诸如'--help'类的特殊选项定义为负数，以获得最先执行的特权。
                如果一次指令没有非零选项，则会执行默认动作参数。

        返回:
            无

        异常：
            无
        """
        self.priority = priority
        return

    def check(self,args:list):
        """ 检查函数

        这个函数不是抽象的，默认为“检查无参数”，若选项参数不为空，则抛出异常。

        参数：
            args:   选项参数列

        返回:
            无

        异常：
            UnexpectedArgument： 选项参数不为空时抛出
        """
        if len(args) != 0:
            raise UnexpectedArgument(args[0])
        return

    @abstractmethod
    def execute(self,args:list):
        """
        参数：
            args:   选项参数列
                为了避免check和execute两次重复识别可能导致的性能浪费，可以选择在子
                类中使用成员变量check标记，并在check中将结果保存到对象数据中。

        返回:
            无

        异常：
            无
        """
        pass


class Parser:
    """解析器类

    此类为对指令参数解析器的抽象。
    
    在解析器对象初始化之后，按如下流程处理一条指令：
        调用parse解析指令列表
        调用check检查指令合法性（可选）
        调用execute执行指令列表

    调用auto_process或使用重载的调用运算符自动进行流程，并处理所有相关异常
    """

    class OptionBlock:
        def __init__(self,option:Option,args:list):
            self.option = option
            self.args = args
            return
    

    def __init__(self,
                 option_map:dict,
                 default_execute_option:Option,
                 blank_arguments_proc):
        """
        参数：
            option_map: 选项映射
                键为以'-'开头的str，值为Option类型。
                指令映射中必须包含键'-'，值为零位参数的选项对象。

            default_execute_option: 用户没有指定动作选项时的默认动作选项

            blank_arguments_proc:   不带任何参数时调用的处理函数
                与default_option区别在于，在用户没有给出任何参数（包括零位参数）
                时，才会调用此函数。

        返回:
            无

        异常：
            无
        """
        self.option_map = option_map
        self.default_execute_option = default_execute_option
        self.blank_arguments_proc = blank_arguments_proc
        self.option_block_list = []  # 选项块列表
        return


    def parse(self,args:list):
        """解析参数列表

        在处理一次指令时首先调用此函数传入程序参数列。

        参数：
            args:   待解析的程序参数列

        返回:
            无

        异常：
            InvalidOption:  发现指令映射中不存在选项则抛出
        """
        try:
            option_block = Parser.OptionBlock(self.option_map['-'],[])
            for arg in args:
                if arg.startswith('-'):
                    self.option_block_list.append(option_block)
                    option_block = Parser.OptionBlock(self.option_map[arg],[])
                    continue
                option_block.args.append(arg)
            self.option_block_list.append(option_block)
        except KeyError as e:
            raise InvalidOption(e.args[0])
        # 对arg_block_list按优先级排序
        self.option_block_list.sort(key=lambda option_block:
                                    option_block.option.priority)
        return


    def check(self):
        """进行参数检查

        参数：
            无

        返回:
            无

        异常：
            取决于注册的Option类的check函数
        """
        for option_block in self.option_block_list:
            option_block.option.check(option_block.args)
        return


    def execute(self):
        """执行动作列表

        参数：
            无

        返回:
            无

        异常：
            取决于注册的Option类的execute函数
        """
        # 首先检查是否是空指令
        if len(self.option_block_list) == 1 and self.option_block_list[0].args == []:
            self.blank_arguments_proc()
            return
        # 不是空指令则执行
        for option_block in self.option_block_list:
            option_block.option.execute(option_block.args)
            # 若是动作参数则执行完立即结束运行
            if option_block.option.priority != 0:
                return
        # 如果for循环结束则说明没有动作参数，执行默认动作参数
        self.default_execute_option.execute([])
        return


    def clear(self):
        """清理上一次的指令解析数据

        参数：
            无

        返回:
            无

        异常：
            无        
        """
        self.option_block_list.clear()
        return


def auto_process(parser:Parser,sys_argv:list):
    """自动解析、检查、执行并且处理异常

    自动忽略sys_argv[0]

    参数：
        sys_argv:   系统传入参数，即sys.argv

    返回:
        无

    异常：
        不会产生参数相关异常
    """
    try:
        parser.parse(sys_argv[1::])
        parser.check()
        parser.execute()
    except InvalidOption as err:
        print("InvalidOption:",err.args[0])
    except InvalidArgument as err:
        print("InvalidArgument:",err.args[0])
    except MissingArgument as err:
        print("MissingArgument:",err.args[0])
    except UnexpectedArgument as err:
        print("UnexpectedArgument:",err.args[0])
    return


def main():
    """模块测试主函数
    """
    class MainOption(Option):
        def __init__(self, priority):
            return super().__init__(priority)

        def check(self,args):
            print("zero_args checked")
            return

        def execute(self,args):
            print("zero_args:",args)
            return

    class HelpOption(Option):
        def __init__(self):
            super().__init__(-1)
            return
        
        def execute(self,args):
            print("help_proc executed")
            return

    class ReadOption(Option):
        def __init__(self):
            super().__init__(2)
            return

        def execute(self,args):
            print(a)
            return

    class WriteOption(Option):
        def __init__(self):
            super().__init__(3)
            return

        def check(self,args):
            if len(args) != 1:
                raise MissingArgument("write check needs 1 extra arguments")
            return

        def execute(self,args):
            nonlocal a
            a = args[0]
            return

    def blank_proc():
        print("blank_proc executed")
        return

    a = "a is not inited"
    option_map = {"--help":HelpOption(),
                  "-":MainOption(0),
                  "-r":ReadOption(),
                  "-w":WriteOption()}
    p = Parser(option_map,option_map['-r'],blank_proc)
    while(True):
        auto_process(p,input().split())
        p.clear()
    return


if __name__ == "__main__":
    main()
