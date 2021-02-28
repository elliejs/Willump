# Prerequisite Primer: Asyncio
Aynchronous programming tries to solve problems with event update based systems that classic synchronous programming can't gracefully handle. One note to keep in mind that will be discused a little throughout this explanation is that **concurrency** is not **parallelism**. Asynchronous programming defines a lot of tasks that you want to have happen at efficient times instead of the classic in-order programming style of synchronous programming.

**Async programming is concurrent programming**.

Async programming declares a main loop, vaguely hidden from the programmer, called the **event loop**. Many async tasks can be scheduled to be run on the event loop, but *only one task runs at a time*. If you want many tasks to actually run at the *exact same time*, you are looking for parallelism. Luckily, we don't have to actually achieve parallelism to pretend like our program is behaving in a parallel manner. The idea is that if we want to do something that takes a long time, like say reading the entirety of Moby Dick into memory, we should be allowed to do other things that don't rely on actually having that data ready until we need the data.

The basic unit of async programming is the **coroutine**. a coroutine is a function defined with `async def name(arg, arg... arg):` instead of `def name(arg, arg... arg):`.
```py
async def read_moby_dick():
  #imagine this does stuff and takes forever
```

The idea is that we want to:
1) start reading moby dick
2) do some other stuff that doesn't rely on moby dick
3) wait for moby dick to be done loading and use the data

## Actually interacting with coroutines
So what happens if we call a coroutine?
```py
import asyncio
async def read_moby_dick():
    #read moby dick here, takes forever
    print("ok")
    return 'im moby dick'
coroutine_obj = read_moby_dick()
print(coroutine_obj)
#no matter how long i sleep here or wait, 'ok' will never be printed
```
`<coroutine object read_moby_dick at 0x7f26f0a7f940>`
This creates a coroutine object, or a bundle of code that will *at some point in the future* have the answer from `read_moby_dick`. But it hasn't run yet, and it won't until you `await` it.
```py
result = await coroutine
print(result)
```
```
ok
im moby dick
```
In fact, *all* the processing from read_moby_dick is done **and blocking your main loop** in the await statement. "Well then what on earth is this all about?" I hear you cry.

## Tasks, and the whole reason async exists
Tasks are how you actually make the async puzzle come together. When you start a task it gets put off on the back burner to start processing, and you can retrieve its result by awaiting it. Instead of a raw coroutine, lets try making a task:
```py
import asyncio
async def read_moby_dick():
    #read moby dick here, takes forever
    print("ok")
    return 'im moby dick'
task = asyncio.create_task(read_moby_dick())
print(task)
```
```
<Task pending name='Task-2' coro=<read_moby_dick() running at <ipython-input-10-0d41a4b16378>:2>>
ok
```
This printed `ok` without us even awaiting! Tasks begin their execution when you create them, unlike coroutines. To summarize: You define a coroutine with `async def`. you can await a coroutine to block your code and retieve the result, or you can toss the coroutine into a task, and gather the result when you need it with await. **You still need to await tasks to take them off the event loop and verify that you aren't leaving things running**. As you can tell, printing task did not print `im moby dick`.

Full example:
```py
import asyncio
async def read_moby_dick():
    #read moby dick here, takes forever
    print("ok")
    return 'im moby dick'
task = asyncio.create_task(read_moby_dick())
print(task)
print(await task)
```
```
<Task pending name='Task-4' coro=<read_moby_dick() running at <ipython-input-11-528aecf5d37f>:2>>
ok
im moby dick
```
Keep in mind, `await task` still blocks your main loop until the task completes. This is okay however, because we can assume that you await the task at the last moment in your code before you *need* it to finish running so you can use the result in future computation.

## How to run an async program
The top level of a python program is sync. **You cannot use await in a sync function, it's not allowed**, so you need a little help from asyncio to get your async program up and running
```py
import asyncio #necessary library

async def main(): #declaring an async program
  #do async stuff

if __name__ == '__main__':
  #windows
  loop = asyncio.get_event_loop() #get reference to event loop (handled by OS)
  loop.run_until_complete(main()) #in a sync way, run the following async program.
  #run_until_completed doesn't need to be awaited so it can be put in a sync function
  loop.run_until_complete(asyncio.sleep(1)) #fake out your OS to behave
  loop.close() #done with the loop. close

  #sane OS's
  asyncio.run(main()) #yep just run it. ez pz
```

## Connecting async to Willump
Willump dispatches websocket subscription events to the main event loop, keeping track of them but not blocking the websocket loop. In this way there's no blocked downtime receiving websocket events from the LCU server, each handler gets dispatched as the event comes in.
